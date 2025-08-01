import os
import json
import requests
import smtplib
from email.message import EmailMessage

API_URL = "https://www.recreation.gov/api/permitinyo/445859/availabilityv2?start_date=2025-08-01&end_date=2025-08-31&commercial_acct=false"
BOOKING_URL = "https://www.recreation.gov/permits/445859/registration/detailed-availability?date=2025-08-29&type=overnight-permit"
EMAIL_ALERTS = True
EMAIL_FROM = "hayden.util@gmail.com"
EMAIL_TO = "hayden.clev@gmail.com"
EMAIL_PASS = os.environ.get("EMAIL_PASS")
STATE_FILE_NAME = "state.json"
START_DATE = "2025-08-30"
DEFAULT_MAPPING = {
    "44585929": {
        "name": "Mono Meadow",
        "available": 0,  
    },
    "44585934": {
        "name": "Ostrander (Lost Bear Meadow)",
        "available": 0,
    }
}

def check_for_updates(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            "Accept": "application/json",
            "Referer": "https://www.recreation.gov/",
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()["payload"]
    
    except Exception as e:
        print(f"/Error requesting permit information: {e}")
        return []
    
    permits = read_permit_state()
    
    updates = False
    for code, trail in permits.items():
        current = data[START_DATE][code]["quota_usage_by_member_daily"]["remaining"]
        if current != trail["available"]:
            updates = True
            permits[code]["available"] = current
            
    if updates:
        write_permit_state(permits)

    return (permits, updates)

def read_permit_state():
    if os.path.exists(STATE_FILE_NAME):
        print(f"File '{STATE_FILE_NAME}' found. Loading data...")
        try:
            with open(STATE_FILE_NAME, 'r') as f:
                return json.load(f)
            print("Data loaded successfully.")
        except json.JSONDecodeError:
            print(f"Error: '{STATE_FILE_NAME}' is not a valid JSON file. Using default mapping.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}. Using default mapping.")
    else:
        print(f"File '{STATE_FILE_NAME}' not found. Using default mapping.")
    return DEFAULT_MAPPING

def write_permit_state(permits):
    print(f"Writing updated data to '{STATE_FILE_NAME}'...")
    try:
        with open(STATE_FILE_NAME, 'w') as f:
            json.dump(permits, f, indent=4)
        print("Data written successfully.")
    except Exception as e:
        print(f"An error occurred while writing to the file: {e}")

def send_email_alert(permits):
    msg = EmailMessage()
    msg['Subject'] = '🎒 Permit Available on Recreation.gov'
    msg['From'] = EMAIL_FROM
    msg['To'] = EMAIL_TO
    body = "The following permits are available:\n\n"
    for trail in permits.values():
        body += f"- {trail['name']}: {trail['available']} permits available\n"
    body += "\nBook permits here: " + BOOKING_URL
    
    msg.set_content(body)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_FROM, EMAIL_PASS)
            smtp.send_message(msg)
        print("Alert email sent.")
    except Exception as e:
        print(f"Failed to send email: {e}")

if __name__ == "__main__":
    (permits, changes) = check_for_updates(API_URL)
    if changes:
        print("Permits available:", permits)
        if EMAIL_ALERTS:
            send_email_alert(permits)
    else:
        print("No changes to permit availability.")
