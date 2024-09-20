import os
import re
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

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

def create_event(service, calendar_id, date, start_time, end_time, class_title):
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
    }
    event = service.events().insert(calendarId=calendar_id, body=event).execute()
    print(f'Event created: {event["summary"]} at {event["start"]["dateTime"]} to {event["end"]["dateTime"]}')

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

def main():
    service = authenticate_google_calendar()
    calendar_id = 'primary'
    
    with open('schedule.html', 'r', encoding='utf-8') as file:
        lines = file.readlines()

    current_date = None
    date = None
    class_title = None
    start_time = None
    end_time = None

    for line in lines:
        line = line.strip()

        if line.startswith("Date:"):
            current_date = extract_date(line)
            print(f"Detected date: {current_date}")

        elif line.startswith("Class:"):
            class_title = extract_class(line)
            print(f"Detected class: {class_title}")

        elif line.startswith("Time range:"):
            time_range = extract_time_range(line)
            if time_range:
                start_time, end_time = time_range
                print(f"Detected time range: {start_time} - {end_time}")
            
            if current_date and start_time and end_time and class_title:
                # Use current_date instead of resetting date.
                create_event(service, calendar_id, current_date, start_time, end_time, class_title)
                print(f"Created event for {class_title} on {current_date} from {start_time} to {end_time}")

            # Reset class and time for the next event but keep the same date
            class_title, start_time, end_time = None, None, None

if __name__ == '__main__':
    main()
