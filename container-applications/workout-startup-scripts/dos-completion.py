#!/usr/bin/python3
import requests
import psutil
from subprocess import Popen, PIPE

dns_suffix = Popen(['sudo', 'printenv', 'DNS_SUFFIX'], stdout=PIPE).stdout.read().decode()
URL = f"https://buildthewarrior{dns_suffix.rstrip()}/complete"


def check_cpu_usage():
    current_cpu_percent = psutil.cpu_percent(interval=1)
    if current_cpu_percent >= 15.0:
        return True
    else:
        return False


def publish():
    # Get values from Environment Variables
    TOKEN = Popen(['sudo', 'printenv', 'WORKOUTKEY0'], stdout=PIPE).stdout.read().decode()
    WORKOUT_ID = Popen(['sudo', 'printenv', 'WORKOUTID'], stdout=PIPE).stdout.read().decode()

    workout = {
        "workout_id": WORKOUT_ID.rstrip(),
        "token": TOKEN.rstrip(),
    }

    publish = requests.post(URL, json=workout)


if check_cpu_usage():
    publish()
    print("Workout Complete")
else:
    print("Incomplete")
