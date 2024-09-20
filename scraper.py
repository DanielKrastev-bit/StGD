from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
import credentials
import re

week = 38 #TODO get curretn week and get next 5 weeks
username = credentials.username
password = credentials.password
chrome_driver_path = "/usr/local/bin/chromedriver"
chrome_options = Options()
#chrome_options.add_argument("--headless")
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)


def login():
    driver.get(f"https://app.shkolo.bg")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "login-username")))
    username_input = driver.find_element(By.ID, "login-username")
    password_input = driver.find_element(By.ID, "passwordField")
    username_input.send_keys(username)
    password_input.send_keys(password)
    password_input.send_keys(Keys.RETURN)

def clear_file(): #TODO create diffrent files and save older ones
    with open('out.html', 'w') as f:
        print('', file=f)
def get_schedule():
    driver.get(f"https://app.shkolo.bg/ajax/diary/getScheduleForClass?pupilx`_id=2400236422&year=24&week={week}&class_year_id=2400011867&_=1726808278160")

login()
clear_file()
get_schedule()
previous_first_char = None
date = []
time_range = []
try:
    schedule_table = driver.find_element(By.CLASS_NAME, "scheduleTable")
    table = schedule_table.find_elements(By.CLASS_NAME, "scheduleTableColumn")
    for columns in table:
        table = columns.find_elements(By.CLASS_NAME, "scheduleTableHeading")
        schedule_date = [row.text for row in table]
        date_pattern = r'\d{2}\.\d{2}\.\d{4}'
        for row in schedule_date:
            match = re.search(date_pattern, row)
            if match:
                date = match.group()
        table = columns.find_elements(By.CLASS_NAME, "scheduleTableBody")
        schedule_body = [row.text for row in table]
        schedule_body = ''.join(schedule_body)
        lines = schedule_body.split('\n')
        with open('out.html', 'a') as f:
            print(f"Date: {date}\n", file=f)
            for line in lines:
                current_first_char = line[0]
                if current_first_char != previous_first_char:
                    time_pattern = r'\d{2}:\d{2} - \d{2}:\d{2}'
                    match = re.search(time_pattern, line)
                    if match:
                        time_range = match.group()
                    print(f"Class: {line}\n Time range: {time_range}", file=f)
                    previous_first_char = current_first_char

 


except Exception as e:
    print(f"Error: {e}")

driver.quit()