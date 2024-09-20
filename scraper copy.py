from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import credentials

# Replace these with your own Shkolo.bg credentials
username = credentials.username
password = credentials.password

# Path to ChromeDriver
chrome_driver_path = "/usr/local/bin/chromedriver"

# Set up the Chrome WebDriver
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service)

# Open the Shkolo.bg login page
driver.get("https://app.shkolo.bg/login")

# Wait for the username input to be present
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "login-username")))

# Find and input login credentials
username_input = driver.find_element(By.ID, "login-username")
password_input = driver.find_element(By.ID, "passwordField")

# Enter the username and password
username_input.send_keys(username)
password_input.send_keys(password)

# Submit the login form
password_input.send_keys(Keys.RETURN)

# Navigate to the schedule page
driver.get("https://app.shkolo.bg/ajax/diary/getScheduleForClass?pupilx`_id=2400236422&year=24&week=38&class_year_id=2400011867&_=1726808278160")

# After navigating to the schedule page
WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "scheduleTable")))

# Clear output file
with open('out.html', 'w') as f:
    print('', file=f) 

# Extract schedule data from the page
try:
    schedule_table = driver.find_element(By.CLASS_NAME, "scheduleTable")  # Find the schedule table

    # Find all rows of the schedule table
    cols = schedule_table.find_elements(By.CLASS_NAME, "scheduleTableColumn")

    # Parse and print each row of the schedule
    for col in cols:
        cols = col.find_elements(By.CLASS_NAME, "scheduleTableHeading")  # Get columns in the row
        schedule_data = [row.text for row in cols]  # Extract text from each column
        print(schedule_data)
        with open('out.html', 'a') as f:
            print(schedule_data, file=f) 

except Exception as e:
    print(f"An error occurred while scraping the schedule: {e}")


# Close the browser
driver.quit()