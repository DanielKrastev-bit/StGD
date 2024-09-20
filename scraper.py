from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
import credentials
import re
import os
import datetime

# Global Variables
username = credentials.username
password = credentials.password
chrome_driver_path = "/usr/local/bin/chromedriver"
chrome_options = Options()
chrome_options.add_argument("--headless")
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)
today = datetime.datetime.today()
current_week = today.isocalendar()[1]
numer_weeks = 5

def login():
    """Logs into the Shkolo app using provided credentials."""
    driver.get("https://app.shkolo.bg")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "login-username")))
    username_input = driver.find_element(By.ID, "login-username")
    password_input = driver.find_element(By.ID, "passwordField")
    username_input.send_keys(username)
    password_input.send_keys(password)
    password_input.send_keys(Keys.RETURN)

def create_unique_file_name():
    return "schedule.html"

def get_schedule(week):
    """Fetches the schedule page for a specific week."""
    url = (f"https://app.shkolo.bg/ajax/diary/getScheduleForClass?"
           f"pupilx_id=2400236422&year=24&week={week}&class_year_id=2400011867")
    driver.get(url)

def extract_schedule_data(file_name):
    """Extracts the schedule data and writes it to the output file for each week."""
    for week in range(current_week, current_week + numer_weeks):
        # print(f"Fetching schedule for week: {week}")
        get_schedule(week)  # Get schedule for the current week
        
        previous_first_char = None
        date = None
        time_range = None
        last_class_time_range = None

        try:
            schedule_table = driver.find_element(By.CLASS_NAME, "scheduleTable")
            columns = schedule_table.find_elements(By.CLASS_NAME, "scheduleTableColumn")

            with open(file_name, 'a', encoding='utf-8') as f:
                for column in columns:
                    # Extract Date
                    heading_elements = column.find_elements(By.CLASS_NAME, "scheduleTableHeading")
                    schedule_date = [row.text for row in heading_elements]
                    date = extract_date(schedule_date)

                    # Extract Class Time and Schedule
                    body_elements = column.find_elements(By.CLASS_NAME, "scheduleTableBody")
                    schedule_body = ''.join([row.text for row in body_elements])
                    lines = schedule_body.split('\n')

                    # Write extracted data
                    f.write(f"Date: {date}\n")
                    for line in lines:
                        current_first_char = line[0]
                        if current_first_char != previous_first_char:
                            time_range = extract_time_range(line)

                            # Remove the last time range from the class line
                            class_info = re.sub(r' \d{2}:\d{2} - \d{2}:\d{2}$', '', line).strip()

                            # Store the last class time range
                            last_class_time_range = time_range

                            f.write(f"Class: {class_info}\nTime range: {time_range}\n")
                            previous_first_char = current_first_char
        except Exception as e:
            print(f"Error: {e}")

def extract_date(schedule_date):
    """Extracts the date from a given schedule date string using regex."""
    date_pattern = r'\d{2}\.\d{2}\.\d{4}'
    for row in schedule_date:
        match = re.search(date_pattern, row)
        if match:
            return match.group()
    return None

def extract_time_range(line):
    """Extracts the time range from a schedule line using regex."""
    time_pattern = r'\d{2}:\d{2} - \d{2}:\d{2}'
    match = re.search(time_pattern, line)
    return match.group() if match else "08:00 - 13:55"

def main():
    try:
        login()
        delete_schedule_file('schedule.html')
        file_name = create_unique_file_name()
        extract_schedule_data(file_name)
        
    finally:
        driver.quit()

def delete_schedule_file(file_path):
    if os.path.exists(file_path): 
        os.remove(file_path)

# Run the main function
if __name__ == "__main__":
    main()
