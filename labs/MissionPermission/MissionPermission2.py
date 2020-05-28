#!/usr/bin/python3
import os
import time
from time import localtime, strftime
import logging

filename = '/usr/local/etc/protect_me/vulnerable.txt'
log_file = "/usr/local/src/workout/MissionPermissions2/MissionPermissions2.log"


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

        elif event == 'Redundant':
            logging.info(' {} : Workout Has already been completed'.format(event_time))


def check_linux_perm():
    status = os.stat(filename)
    permissions = oct(status.st_mode)[-3:]
    
    if permissions == '740':
        print("[+] Permisions: {} --> I'm Secure!".format(permissions))
        return True
    else:
        print("[+] Permissions: {} --> Still vulnerable! ".format(permissions))
        return False


def verify():
    complete = '/usr/local/src/workout/MissionPermissions2/MissionPermissions2-Status.txt'
    with open(complete) as f:
        if 'Complete' in f.read():
            return True
        else:
            return False

# check_linux = check_linux_perm()
if not verify():
    if check_linux_perm():
        log('Complete')
        os.system('python3 /usr/local/bin/cg-publish.py missionpermissions2')
    else:
        log('Incomplete')
else:
    log('Redundant')