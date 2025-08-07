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

Coming soon...

Github Actions claims that they provide scheduling at 5min intervals, but in practice this is unreliable and can have gaps in execution in excess of one hour. Instead, it is best to use a free online cron job scheduler such as [cron-job.org](cron-job.org) to manually trigger the action via a POST call. A writeup on how to achieve this can be acccessed [here](https://docs.github.com/en/rest/actions/workflows?apiVersion=2022-11-28#create-a-workflow-dispatch-event).

The example `curl` command below can be translated into cron-job UI:
```
curl -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: token ${GH_PAT}" \
  https://api.github.com/repos/haydenclev/permit-alert/actions/workflows/schedule.yml/dispatches \
  -d '{"ref": "main"}'
```

## Limitations

Currently this only works for permits in Yosemite National Park. If you are interested in other recreation areas please get in touch or become a contributor!