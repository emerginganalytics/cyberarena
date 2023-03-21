#!/usr/bin/python3
import os
import time
import requests
import psutil


class Assessment:
    QUESTION_NUMBER = '1'
    URL_PREFIX = os.environ.get('URL')
    BUILD_ID = os.environ.get('build_id')
    URL = f'{URL_PREFIX}{BUILD_ID}'


def assess():
    last_reboot = psutil.boot_time()
    current_time = time.time()
    if current_time - last_reboot > 300:
        current_cpu_percent = psutil.cpu_percent(interval=1)
        if current_cpu_percent >= 70.0:
            return True
    return False


def mark_complete():
    complete_file = 'signal_complete'
    url = os.environ.get(Assessment.URL)
    q_key = os.environ.get(f'Q{Assessment.QUESTION_NUMBER}_KEY')
    data = {
        'question_id': q_key,
    }
    response = requests.put(url, json=data)
    if response and response.status_code == 200:
        open(complete_file, 'a').close()


if __name__ == '__main__':
    if assess():
        mark_complete()
        print('Workout Complete')
    else:
        print("Incomplete")
