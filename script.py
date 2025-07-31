import os
import requests
import smtplib
from email.message import EmailMessage

URL = "https://www.recreation.gov/api/permitinyo/445859/availabilityv2?start_date=2025-08-01&end_date=2025-08-31&commercial_acct=false"
EMAIL_ALERTS = True
EMAIL_FROM = "hayden.util@gmail.com"
EMAIL_TO = "hayden.clev@gmail.com"
EMAIL_PASS = os.environ.get("EMAIL_PASS")
START_DATE = "2025-08-29"
TH_MAPPING = {
    "Mono Meadow": "44585929",
    "Ostrander (Lost Bear Meadow)": "44585934"
}

def check_availability(url):
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

    available = []
    for name, code in TH_MAPPING.items():
        remaining = data[START_DATE][code]["quota_usage_by_member_daily"]["remaining"]
        if remaining > 2:
            available.append((name, remaining))

    return available


def send_email_alert(permits):
    msg = EmailMessage()
    msg['Subject'] = '🎒 Permit Available on Recreation.gov'
    msg['From'] = EMAIL_FROM
    msg['To'] = EMAIL_TO
    body = "The following permits are available:\n\n"
    for trailhead, available in permits:
        body += f"- {trailhead}: {available} permits available\n"
    body += "\nBook permits here: https://www.recreation.gov/permits/445859/registration/detailed-availability?date=2025-08-29&type=overnight-permit"
    
    msg.set_content(body)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_FROM, EMAIL_PASS)
            smtp.send_message(msg)
        print("Alert email sent.")
    except Exception as e:
        print(f"Failed to send email: {e}")

if __name__ == "__main__":
    available = check_availability(URL)
    if available:
        print("Permits available:", available)
        if EMAIL_ALERTS:
            send_email_alert(available)
    else:
        print("No permits available.")
