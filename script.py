import os
import json
import yaml
import requests
import smtplib
from dotenv import load_dotenv
from email.message import EmailMessage
from pydantic import BaseModel


class Config(BaseModel):
    api_url: str
    web_url: str
    start_date: str
    state_file: str
    default_state: dict
    email_alerts: bool
    email_from: str
    email_to: str


with open("config.yaml") as stream:
    config = Config(**yaml.safe_load(stream))


def check_for_updates(url) -> tuple:
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
        return ()

    permits = read_permit_state()

    updates = False
    for code, trail in permits.items():
        current = data[config.start_date][code]["quota_usage_by_member_daily"]["remaining"]
        if current != trail["available"]:
            updates = True
            permits[code]["available"] = current

    if updates or not os.path.exists(config.state_file):
        write_permit_state(permits)

    return (permits, updates)


def read_permit_state() -> dict:
    if os.path.exists(config.state_file):
        print(f"File '{config.state_file}' found. Loading data...")
        try:
            with open(config.state_file, "r") as f:
                return json.load(f)
            print("Data loaded successfully.")
        except json.JSONDecodeError:
            print(f"Error: '{config.state_file}' is not a valid JSON file. Using default mapping.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}. Using default mapping.")
    else:
        print(f"File '{config.state_file}' not found. Using default mapping.")
    return config.default_state


def write_permit_state(permits) -> None:
    print(f"Writing updated data to '{config.state_file}'...")
    try:
        with open(config.state_file, "w") as f:
            json.dump(permits, f, indent=4)
        print("Data written successfully.")
    except Exception as e:
        print(f"An error occurred while writing to the file: {e}")


def send_email_alert(permits) -> None:
    msg = EmailMessage()
    msg["Subject"] = "🎒 Permit Available on Recreation.gov"
    msg["From"] = config.email_from
    msg["To"] = config.email_to
    body = "The following permits are available:\n\n"
    for trail in permits.values():
        body += f"- {trail['name']}: {trail['available']} permits available\n"
    body += "\nBook permits here: " + config.web_url

    msg.set_content(body)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(config.email_from, os.environ.get("EMAIL_PWD") or "")
            smtp.send_message(msg)
        print("Alert email sent.")
    except Exception as e:
        print(f"Failed to send email: {e}")


if __name__ == "__main__":
    load_dotenv()
    (permits, changes) = check_for_updates(config.api_url)
    if changes:
        print("Permits available:", permits)
        if config.email_alerts:
            send_email_alert(permits)
    else:
        print("No changes to permit availability.")
