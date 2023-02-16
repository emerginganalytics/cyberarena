#!/usr/bin/python3
import os
import time
import requests
import pwd
import subprocess

class Assessment:
    QUESTION_NUMBER = "0"
    USER_CHECK = 'gigabyte'
    OLD_SOFTWARE = "liblog4j2-java/bionic,now 2.10.0-2"
    FILETYPE_CHECK = 'mp4'
    ADMIN_CHECK = 'philip'
    SUDOERS_STRING = "(ALL : ALL) ALL"
    CRONTAB_STRING = "philip    ALL=(ALL:ALL) ALL"



def assess():
    # Vuln 1: Delete Gigabyte User
    for p in pwd.getpwall():
        if p[0] == Assessment.USER_CHECK:
            return False

    # Vuln 2: Log4j
    output = subprocess.run(['apt', 'list', '--installed'], stdout=subprocess.PIPE).stdout.decode('utf-8')
    for line in output.split('\n'):
        if line.startswith(Assessment.OLD_SOFTWARE):
            return False
    
    # Vuln 3: Over-priveleged User
    output = subprocess.run(["sudo", "-l", "-U", Assessment.ADMIN_CHECK], capture_output=True, text=True)
    if Assessment.SUDOERS_STRING in output.stdout:
        return False

    # Vuln 4: Banned File Type
    output = subprocess.run(["find", "/", "-type", "f", "-name", "*.mp4"], capture_output=True, text=True)
    if Assessment.FILETYPE_CHECK in output.stdout:
        return False

    # Vuln 5: Crontab
    output = subprocess.run(["cat", "/var/spool/cron/crontabs/root"], capture_output=True, text=True)
    if Assessment.CRONTAB_STRING in output.stdout:
        return False

    return True


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
