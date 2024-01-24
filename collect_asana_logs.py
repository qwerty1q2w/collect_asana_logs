#!/usr/bin/python3
import json
import requests
import sys
import os
import configparser

config = configparser.ConfigParser()
config.read('config')

org_id = config['asana']['org_id']
token = config['asana']['token']
log_path = config['asana']['log_path']
counter_file_path = config['asana']['counter_file_path']


counter_file = open(counter_file_path)
cursor = counter_file.read().replace("\n","")
counter_file.close()

url = 'https://app.asana.com/api/1.0/workspaces/%s/audit_log_events?offset=%s' % (org_id,cursor)
#url = 'https://app.asana.com/api/1.0/workspaces/%s/audit_log_events' % (org_id) ### use when offset is expired. Once

headers = {'Authorization': 'Bearer %s' % token, 'Accept': 'application/json'}

response = requests.get(url, headers=headers)
#print(response.text)
#print(response.status_code)
if response.status_code == 200:
    ss = response.json()
    if len(ss['data']) > 0:
        for i in ss['data']:
            with open(log_path, 'a') as f:
                f.write(json.dumps(i) + '\n')
        f.close()

else:
#    print(response.text)
    sys.exit()

with open(counter_file_path, 'w') as counter_file:
        counter_file.write(ss['next_page']['offset'])
counter_file.close()
