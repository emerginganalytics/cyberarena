#!/usr/bin/python3
import os
import re
import requests


class Assessment:
    QUESTION_NUMBER = "0"
    LOG_FILE = '/var/log/auth.log'
    LOGIN_CHECK = 'Accepted publickey for cyberarena'
    SSH_CONFIG_FILE = '/etc/ssh/sshd_config'
    SSH_CONFIG_CHECK = 'PasswordAuthentication no'


def assess():
    if _assess_file(Assessment.LOG_FILE, Assessment.LOGIN_CHECK):
        if _assess_file(Assessment.SSH_CONFIG_FILE, Assessment.SSH_CONFIG_CHECK):
            return True
    return False


def _assess_file(file, pattern):
    is_complete = False
    with open(file, "r") as f:
        for line in f:
            if re.search(pattern, line):
                is_complete = True
                break
    return is_complete


def mark_complete():
    complete_file = "signal_complete"

    if not os.path.exists(complete_file):
        url = os.environ.get('URL')
        q_key = os.environ.get(f'Q{Assessment.QUESTION_NUMBER}_KEY')
        build_id = os.environ.get('BUILD_ID')

        data = {
            "question_id": q_key,
        }
        response = requests.put(f"{url}{build_id}", json=data)
        if response and response.status_code == 200:
            open(complete_file, 'a').close()


if assess():
    mark_complete()
    print("Workout Complete")
else:
    print("Incomplete")
