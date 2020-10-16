import os
import requests
import sys

def verify():
    target_file = "/var/www/PhishPhactor/.env"
    with open(target_file) as f:
        if 'Complete' in f.read():
            return False
        else:
            return True

def publish():
    TOKEN = os.environ.get('WORKOUTKEY0')
    WORKOUT_ID = os.environ.get('WORKOUTID')
    DNS_SUFFIX = os.environ.get('DNS_SUFFIX')
    URL = 'https://buildthewarrior{}/complete'.format(DNS_SUFFIX)
    
    workout = {
            "workout_id": WORKOUT_ID,
            "token": TOKEN,
    }
    if verify():
        publish = requests.post(URL, json=workout)
    else:
        sys.exit()