# Permit Alert

This repo is to automate checking for wilderness permits via Recreation.gov. Options to run locally as well in Github Actions are available.

## Running Locally

Create a file named `config.yaml` to house the alert configuration with the following fields:
```
api_url: str
web_url: str
start_date: str
state_file: str
default_state: object
email_alerts: bool
email_from: str
email_to: str
```
Also see `example-config.yaml` for additional information.

To enable email alerts you will need to create an [app password](https://support.google.com/mail/answer/185833?hl=en) and add it to a `.env` file like so:
```
EMAIL_PWD='your email app password here'
```
To run locally:
```
python3 script.py
```
To run every minute:
```
while true; do python3 script.py; sleep 60; done

```

## Running in Github Actions

Users may want a way to run this alert continuously without keeping an open terminal on their machine. To this end the `.github/workflows/schedule.yaml` file has been provided to run in Github Actions. 

### State

Create a branch titled `gh-actions-state` and create a `state.json` file with your desired default config. If you have successfully run the app locally one has already been created for you. Add, commit and push this file (and nothing else) before returning to the `main` branch.

### Personal Access Token

To trigger the workflow via the API you will need to create a personal access token. Follow the steps [here](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-fine-grained-personal-access-token) and be sure to scope it to the appropriate repository and add read + write access. 

### Repository Secrets

To access secrets like your personal access token and email password you will need to add them as repository secrets. Follow instructions [here](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets). Be sure to use the keys `GH_PAT` and `EMAIL_PWD`.

### Scheduling

The workflow can be triggered several ways including manually through the UI (great for testing), through a Github Actions scheduler (problematic), and also (and most importantly) through a HTTP POST request.
Github claims that they provide scheduling at 5min intervals, but in practice this is unreliable and can have gaps in execution in excess of one hour. Instead, it is best to use a free online cron job scheduler such as [cron-job.org](cron-job.org) to manually trigger the action via a POST call.

The request itself should include the following input fields:
- `trigger`: Triggering mechanism (e.g. UI or Cron Job). Used to enhance the Github UI.
- `config`: Configuration object similar to that when running locally, but with a different path for the `state_file`. Example request is provided below.

Example `curl` command below:
```
curl -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: token ${GH_PAT}" \
  https://api.github.com/repos/haydenclev/permit-alert/actions/workflows/schedule.yml/dispatches \
    -d '{
    "ref": "main",
    "inputs": {
      "trigger": "API",
      "config": "api_url: \"https://www.recreation.gov/api/permitinyo/445859/availabilityv2?start_date=2025-08-01&end_date=2025-08-31&commercial_acct=false\"\nweb_url: \"https://www.recreation.gov/permits/445859/registration/detailed-availability?date=2025-08-29&type=overnight-permit\"\nstart_date: \"2025-08-30\"\nstate_file: \"state.json\"\ndefault_state:\n  44585929:\n    name: \"Mono Meadow\"\n    available: 0\n  44585934:\n    name: \"Ostrander (Lost Bear Meadow)\"\n    available: 0\nemail_alerts: true\nemail_from: \"${sender@gmail.com}$\"\nemail_to: \"${receiver@gmail.com}$\""
    }
  }'
    }
  }'
```

## Limitations

Currently this only works for permits in Yosemite National Park. If you are interested in other recreation areas please get in touch or become a contributor!