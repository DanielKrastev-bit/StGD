# StGD - Shkolo Schedule to Google Drive

StGD is a Python-based tool that automates the process of scraping class schedules from Shkolo.bg and storing them in Google Calendar as tasks.

## Features
- **Automated login**: Logs into Shkolo.bg using your credentials.
- **Schedule scraping**: Fetches the weekly schedule for a specific period.
- **Headless mode**: Runs the browser in headless mode for seamless automation.
- **File storage**: directly into Google Calendar.
- **Error handling**: Safely handles errors and ensures the browser is closed after execution.

## Prerequisites

- **Python 3.x**
- **Selenium**: Install using `pip install selenium`
- **ChromeDriver**: [Download ChromeDriver](https://developer.chrome.com/docs/chromedriver/downloads) and ensure it is in your system's `PATH`.
- **Google Chrome**: Ensure you have Google Chrome installed.
- **Google API setup for Drive access**

## Setup

1. Clone the repository:

```bash
git clone https://github.com/DanielKrastev-bit/StGD.git
cd StGD
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```
Download and place the ChromeDriver executable in /usr/local/bin/ or any path available in your system. You can also update the chrome_driver_path in the script if ChromeDriver is located elsewhere.

3. Create a `credentials.py` file in the project directory containing your Shkolo.bg username and password:

```python
# credentials.py
username = "your_username"
password = "your_password"
```
4. Configure Google Drive API for Drive access. Follow Google's quickstart guide for instructions.

5. Place your ChromeDriver in `/usr/local/bin/` or update the path in `scraper.py`.


## Usage
**Update the week variable in the script to match the current week or implement an automatic way to calculate it.**
Run the script:

```bash
python shkolo_scraper.py
```
**The schedule for the specified week will be saved in an HTML file with a unique name based on the current timestamp, located in the project directory.**


**Planned Improvements**
**Automatically calculate and scrape the current week and the following 5 weeks.**
**Additional error handling for network or authentication issues.**
**Support for saving older schedules in a dedicated folder.**
**Multi-class and multi-user support.**

## License
This project is licensed under the GNU General Public License v3.0. See the LICENSE file for more details.