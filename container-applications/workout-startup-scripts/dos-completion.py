#!/usr/bin/python3
import os
import requests
import psutil
from subprocess import check_output

dns_suffix = check_output(['sudo', 'printenv', 'DNS_SUFFIX'], universal_newlines=True).strip()
url = f"https://buildthewarrior{dns_suffix}/complete"


def check_cpu_usage():
    current_cpu_percent = psutil.cpu_percent(interval=1)
    if current_cpu_percent >= 15.0:
        return True
    else:
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
