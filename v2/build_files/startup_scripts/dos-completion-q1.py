#!/usr/bin/python3
import os
import time
import requests
import psutil


class Assessment:
    QUESTION_NUMBER = '0'
    URL_PREFIX = os.environ.get('URL')
    BUILD_ID = os.environ.get('BUILD_ID')
    URL = f'{URL_PREFIX}{BUILD_ID}'


def assess():
    last_reboot = psutil.boot_time()
    current_time = time.time()
    if current_time - last_reboot > 300:
        current_cpu_percent = psutil.cpu_percent(interval=1)
        print(current_cpu_percent)
        if current_cpu_percent >= 40.0:
            return True
    return False


def mark_complete():
    q_key = os.environ.get(f'Q{Assessment.QUESTION_NUMBER}_KEY')
    data = {
        'question_id': q_key,
    }
    response = requests.put(Assessment.URL, json=data)
    if response and response.status_code == 200:
        print('Workout Complete!')


if __name__ == '__main__':
    if assess():
        mark_complete()
    else:
        print('Incomplete')
