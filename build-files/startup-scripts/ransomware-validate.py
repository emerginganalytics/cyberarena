#!/usr/bin/python3
import base64
import requests
import os
import sys

"""
Ransomware-Validate is used for the ransomware workout for automatically verifying when the workout completes.
This script is copied into the nekros ransomware. It is not added to the startup file

"""
URL = os.environ.get('URL')
TOKEN = os.environ.get('WORKOUTKEY0')
WORKOUT_ID = os.environ.get('WORKOUTID')

workout = {
    "workout_id": WORKOUT_ID,
    "token": TOKEN,
}

publish = requests.post(URL, json=workout)
print('[*] POSTING to {} ...'.format(URL))
print(publish)

print('finished')
