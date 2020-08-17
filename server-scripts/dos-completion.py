#!/usr/bin/python3
import os
import requests
import psutil

url = "https://buildthewarrior.cybergym-eac-ualr.org/complete"


def check_cpu_usage():
    current_cpu_percent = psutil.cpu_percent(interval=1)
    if current_cpu_percent >= 30.0:
        publish()
    else:
        print("Incomplete")


def publish():
    token = os.environ.get('WORKOUTKEY0')
    workout_id = os.environ.get('WORKOUTID')

    workout = {
        "workout_id": workout_id,
        "token": token,
    }

    publish = requests.post(url, json=workout)
