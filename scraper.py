from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
import credentials
import re


# Global Variables
week = 40  # TODO: Automatically get the current week and the next 5 weeks
username = credentials.username
password = credentials.password
chrome_driver_path = "/usr/local/bin/chromedriver"
chrome_options = Options()
chrome_options.add_argument("--headless")
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)


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
    #timestamp = time.strftime("%Y%m%d-%H%M%S")
    #return f"schedule_{timestamp}.html"
    return "schedule.html"

def get_schedule():
    # Fetches the schedule page for a specific week.
    url = (f"https://app.shkolo.bg/ajax/diary/getScheduleForClass?"
           f"pupilx_id=2400236422&year=24&week={week}&class_year_id=2400011867")
    driver.get(url)

def extract_schedule_data(file_name):
    # Extracts the schedule data and writes it to the output file.
    previous_first_char = None
    date = None
    time_range = None

    try:
        schedule_table = driver.find_element(By.CLASS_NAME, "scheduleTable")
        columns = schedule_table.find_elements(By.CLASS_NAME, "scheduleTableColumn")
        
        with open(file_name, 'a') as f:
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
                        f.write(f"Class: {line}\nTime range: {time_range}\n")
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
    return match.group() if match else None

def main():
    try:
        login()
        file_name = create_unique_file_name()
        get_schedule()
        extract_schedule_data(file_name)
        
    finally:
        driver.quit()

# Run the main function
if __name__ == "__main__":
    main()
