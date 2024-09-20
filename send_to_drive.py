import os
import re
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Define a list of possible colors (these are Google Calendar color IDs)
COLORS = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11"]
calendar_id = 'b8779324f29d709c197598ff6c362082049204000bdbceb809d85101f91d578a@group.calendar.google.com'

def authenticate_google_calendar():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=8080)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('calendar', 'v3', credentials=creds)

def create_event(service, date, start_time, end_time, class_title, color_id):
    event = {
        'summary': class_title,
        'start': {
            'dateTime': f'{date}T{start_time}:00',
            'timeZone': 'Europe/Sofia',
        },
        'end': {
            'dateTime': f'{date}T{end_time}:00',
            'timeZone': 'Europe/Sofia',
        },
        'colorId': color_id,
        'description': 'Created by my_script',  # Tag for identification
    }
    
    event = service.events().insert(calendarId=calendar_id, body=event).execute()
    print(f'Event created: {event["summary"]} at {event["start"]["dateTime"]} to {event["end"]["dateTime"]}, Color ID: {color_id}')

def extract_date(line):
    match = re.search(r'Date: (\d{2}\.\d{2}\.\d{4})', line)
    if match:
        return datetime.strptime(match.group(1), '%d.%m.%Y').strftime('%Y-%m-%d')
    return None

def extract_class(line):
    match = re.search(r'Class: (.+)', line)
    if match:
        return match.group(1)
    return None

def extract_time_range(line):
    match = re.search(r'Time range: (\d{2}:\d{2}) - (\d{2}:\d{2})', line)
    if match:
        return match.group(1), match.group(2)
    return None

def time_to_minutes(time_str):
    """Convert time string (HH:MM) to minutes since midnight."""
    hours, minutes = map(int, time_str.split(':'))
    return hours * 60 + minutes

def minutes_to_time(minutes):
    """Convert minutes since midnight back to time string (HH:MM)."""
    hours = minutes // 60
    minutes = minutes % 60
    return f'{hours:02}:{minutes:02}'

def get_color_for_class(class_title, class_color_map):
    """Assign a color to a class if not already assigned."""
    if class_title not in class_color_map:
        color_index = len(class_color_map) % len(COLORS)
        class_color_map[class_title] = COLORS[color_index]
    return class_color_map[class_title]

def main():
    service = authenticate_google_calendar()
    calendar_id = 'primary'
    
    with open('schedule.html', 'r', encoding='utf-8') as file:
        lines = file.readlines()

    current_date = None
    class_title = None
    start_time = None
    end_time = None
    last_end_time = None
    combined_class_title = None
    event_created_for_day = False  # Track if at least one event was created for the day

    class_color_map = {}  # To map each class to a specific color

    for line in lines:
        line = line.strip()

        if line.startswith("Date:"):
            # Create the last event for the previous date if needed
            if combined_class_title and start_time and end_time:
                color_id = get_color_for_class(combined_class_title, class_color_map)
                create_event(service, current_date, start_time, end_time, combined_class_title, color_id)

            # New date starts, reset tracking
            current_date = extract_date(line)
            print(f"Detected date: {current_date}")
            class_title, start_time, end_time, last_end_time = None, None, None, None
            combined_class_title = None
            event_created_for_day = False

        elif line.startswith("Class:"):
            new_class_title = extract_class(line)
            print(f"Detected class: {new_class_title}")

        elif line.startswith("Time range:"):
            time_range = extract_time_range(line)
            if time_range:
                new_start_time, new_end_time = time_range
                print(f"Detected time range: {new_start_time} - {new_end_time}")

                # Combine classes if they are adjacent
                if last_end_time and time_to_minutes(new_start_time) == time_to_minutes(last_end_time):
                    combined_class_title = f"{combined_class_title}, {new_class_title}"
                    end_time = new_end_time
                else:
                    if combined_class_title and start_time and end_time:
                        color_id = get_color_for_class(combined_class_title, class_color_map)
                        create_event(service, current_date, start_time, end_time, combined_class_title, color_id)
                        event_created_for_day = True

                    combined_class_title = new_class_title
                    start_time = new_start_time
                    end_time = new_end_time

                last_end_time = new_end_time

    # Create event for the last class on the last date
    if combined_class_title and start_time and end_time:
        color_id = get_color_for_class(combined_class_title, class_color_map)
        create_event(service, current_date, start_time, end_time, combined_class_title, color_id)
        event_created_for_day = True

    # If no specific events were created for a day, add a default event
    if not event_created_for_day and current_date:
        print(f"No time ranges detected for {current_date}, adding default event from 08:00 to 15:00.")
        create_event(service, calendar_id, current_date, "08:00", "15:00", "No Specific Class", "1")  # Default color

if __name__ == '__main__':
    main()
