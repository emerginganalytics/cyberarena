#!/usr/bin/python3
import os
import time
import requests
import psutil
from subprocess import check_output

dns_suffix = check_output(['sudo', 'printenv', 'DNS_SUFFIX'], universal_newlines=True).strip()
url = f"https://buildthewarrior{dns_suffix}/complete"


def check_cpu_usage():
    current_cpu_percent = psutil.cpu_percent(interval=1)
    if current_cpu_percent >= 40.0:
        return True
    else:
        return False


def publish(question):
    token = os.environ.get(f'WORKOUTKEY{question}')
    workout_id = os.environ.get('WORKOUTID')

    workout = {
        "workout_id": workout_id,
        "token": token,
    }

    publish = requests.post(url, json=workout)


last_reboot = psutil.boot_time()
current_time = time.time()

if current_time - last_reboot > 300:
    if check_cpu_usage():
        publish(question=0)
        print("Workout Complete")
    else:
        print("Incomplete")
