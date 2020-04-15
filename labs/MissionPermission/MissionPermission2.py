#!/usr/bin/python3
import os
import time

def check_linux_perm():
    filename = '/usr/local/etc/protect_me/vulnerable.txt'
    status = os.stat(filename)
    permissions = oct(status.st_mode)[-3:]
    
    if permissions == '740':
        print("[+] Permisions: {} --> I'm Secure!".format(permissions))
        return True
    else:
        print("[+] Permissions: {} --> Still vulnerable! ".format(permissions))
        return False 

# if workout is complete, publish
check_linux = check_linux_perm()
while True:
    if check_linux:
        print('[*] Publishing Results ...')
        os.system('python3 /usr/local/bin/cg-publish.py missionpermissions2')
    else:
        print('[!!] File is still insecure! [!!]')
        time.sleep(180)    
