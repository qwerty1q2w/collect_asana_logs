#!/usr/bin/env python3
import json
import requests
import configparser
from urllib.parse import quote
import datetime

# Get the current date and time in a specific format
dt = datetime.datetime.utcnow()
formatted_date_with_microseconds = dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
now_date = formatted_date_with_microseconds[:-4] + 'Z'
# format 2024-01-25T11:47:11.895Z

# Read configuration file
config = configparser.ConfigParser()
config.read('config')

# Retrieve necessary configuration parameters
org_id = config['asana']['org_id']
token = config['asana']['token']
log_path = config['asana']['log_path']
counter_file_path = config['asana']['counter_file_path']

# Read the last processed time from the counter file
# format 2024-01-25T11:47:11.895Z
with open(counter_file_path, "r") as f:
    last_time = f.read().strip()

# Initial API request to fetch audit log events
url = f'https://app.asana.com/api/1.0/workspaces/{org_id}/audit_log_events?start_at={quote(last_time)}&end_at={quote(now_date)}'
headers = {'Authorization': f'Bearer {token}', 'Accept': 'application/json'}
response = requests.get(url, headers=headers)
data = response.json()
logs = data.get('data', [])
page_token = data.get('next_page', {}).get('offset', None)

# Loop to handle pagination
while page_token:
    url = f'https://app.asana.com/api/1.0/workspaces/{org_id}/audit_log_events?start_at={quote(last_time)}&end_at={quote(now_date)}&offset={page_token}'
    response = requests.get(url, headers=headers)
    data = response.json()
    logs.extend(data.get('data', []))
    page_token = data.get('next_page', {}).get('offset', None)
    if len(data['data']) == 0:
        page_token = None

# Writing logs to the file
with open(log_path, 'a') as log_file:
    for log_entry in logs:
        log_file.write(json.dumps(log_entry) + '\n')

# Update the counter file with the current date
with open(counter_file_path, "w") as f:
    f.write(now_date)
