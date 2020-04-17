#!/usr/bin/python3
import base64 as b64
import requests
import sys

token = "<token_value>"
URL = "https://buildthewarrior.cybergym-eac-ualr.org/complete"

# Parse workout ID from Machine Metatdata
headers = {
    'Metadata-Flavor': 'Google',
}
metadata = requests.get('http://metadata.google.internal/computeMetadata/v1/instance/name', headers=headers)
data = ((metadata.content).decode('utf-8')).split('-')
w_id = data[0]

workout = {
    "workout_id": w_id,
    "token": token,
}

publish = requests.post(URL, json=workout)
print('[*] POSTING to {} ...'.format(URL))
print(publish)
