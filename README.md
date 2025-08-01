# Permit Alert

This repo is to automate checking for wilderness permits via Recreation.gov

## Configuration

Edit the following fields in `script.py` to configure your alert:
- URL: edit the `start_date` and `end_date` fields for your desired timeframe. Note that the API seems to only accept entire month blocks.
- START_DATE: the day you wish to begin your hike
- DEFAULT_MAPPING: provides the starting state for the trailheads you want to monitor. Emails are sent on any changes observed. Retrieve the trailhead codes from the recreation.gov website `features.json` network call.

## Scheduling

Github Actions claims that they provide scheduling at 5min intervals, but in practice this is unreliable and can have gaps in execution in excess of one hour. Instead, it is best to use a free online cron job scheduler such as [cron-job.org](cron-job.org) to manually trigger the action via a POST call. A writeup on how to achieve this can be acccessed [here](https://docs.github.com/en/rest/actions/workflows?apiVersion=2022-11-28#create-a-workflow-dispatch-event).

The example `curl` command below can be translated into cron-job UI:
```
curl -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: token ${GITHUB_PAT}" \
  https://api.github.com/repos/haydenclev/permit-alert/actions/workflows/schedule.yml/dispatches \
  -d '{"ref": "main"}'
```

## Current Alerts

2025-08-29 Illilouette Basin
- [Scheduler](https://console.cron-job.org/jobs/6411246/history)
- [Executions](https://github.com/haydenclev/permit-alert/actions/workflows/schedule.yml)