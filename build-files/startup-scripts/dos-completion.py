#!/usr/bin/python3
import os
import requests
import psutil
from subprocess import check_output
from time import time

dns_suffix = check_output(['sudo', 'printenv', 'DNS_SUFFIX'], universal_newlines=True).strip()
url = f"https://buildthewarrior{dns_suffix}/complete"
boot_time = int(psutil.boot_time())

def check_cpu_usage():
    current_cpu_percent = psutil.cpu_percent(interval=1)
    current_time = int(time.time())

    if current_cpu_percent >= 15.0:
        if current_time >= boot_time + 300:
            return True
    return False

def publish():
    token = os.environ.get('WORKOUTKEY0')
    workout_id = os.environ.get('WORKOUTID')

    workout = {
        "workout_id": workout_id,
        "token": token,
    }

    publish = requests.post(url, json=workout)


if check_cpu_usage():
    publish()
    print("Workout Complete")
else:
    print("Incomplete")
