#!/usr/bin/python3
import logging
import os
import requests
import subprocess
import time
from time import localtime, strftime

filename = '/usr/local/etc/protect_me/vulnerable.txt'
log_file = "/usr/local/src/workout/MissionPermissions2/MissionPermissions2.log"
dns_suffix = subprocess.Popen(['sudo', 'printenv', 'DNS_SUFFIX'])
URL = f"https://buildthewarrior{dns_suffix}/complete"

# Used for debugging
def log(event):
        logging.basicConfig(filename=log_file, level=logging.DEBUG)
        
        status = os.stat(filename)
        permissions = oct(status.st_mode)[-3:]

        event_time = strftime("%H:%M:%S", localtime())
        
        if event == 'Incomplete':
            logging.info(' {} : File is still insecure : Permissions={}'.format(event_time, permissions))
        
        elif event == 'Complete':
            logging.info(' {} : File is secure! : Permissions={}'.format(event_time, permissions))
            update = open('/usr/local/src/workout/MissionPermissions2/MissionPermissions2-Status.txt', 'w')
            update.write('Complete')
            update.close()
        elif event == 'Publish':
            logging.info(' {} : [+] Posting to {} ...'.format(event_time, URL))

        elif event == 'Redundant':
            logging.info(' {} : Workout Has already been completed'.format(event_time))


# Checks file permissions and returns True if workout is complete
def check_linux_perm():
    status = os.stat(filename)
    permissions = oct(status.st_mode)[-3:]
    
    if permissions == '740':
        print("[+] Permisions: {} --> I'm Secure!".format(permissions))
        return True
    else:
        print("[+] Permissions: {} --> Still vulnerable! ".format(permissions))
        return False 


# Used to make sure the Publish call is only used once
def verify():
    complete = '/usr/local/src/workout/MissionPermissions2/MissionPermissions2-Status.txt'
    with open(complete) as f:
        if 'Complete' in f.read():
            return True
        else:
            return False


# Publishes workout completion status
def publish():
    # Get values from Environment Variables
    TOKEN = os.environ.get('WORKOUTKEY0')
    WORKOUT_ID = os.environ.get('WORKOUTID')

    workout = {
        "workout_id": WORKOUT_ID,
        "token": TOKEN,
    }

    publish = requests.post(URL, json=workout)
    log('Publish')

# check_linux = check_linux_perm()
if not verify():
    if check_linux_perm():
        log('Complete')
        publish()
    else:
        log('Incomplete')
else:
    log('Redundant')
