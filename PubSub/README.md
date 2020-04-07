# Pub/Sub Scripts
### This folder contains the code needed to run the pub/sub server

---
---
## [ Requirements ]:
Python3.6 or greater (preferably 3.8)

Python Requirements:
pip3 install -r requirements.txt

PubSub Service .json key:   
```
Go to IAM & Admin > Service Accounts > cybergym-publisher@... > edit > create key
```
Even though this key only has access to Publish to the Cloud, be sure to store it in a safe place.

**Currently, cg-publish and .json are stored in these directories:**
  ```
  Linux dir = /usr/local/bin/cg-publish.py | /usr/local/lib/...json
  Windows = C:\Data\Pub\[both .py and .json]
  ```
## [ cg-publish.py ]:   
This script can be used with any workout. In order for the script to work properly, you'll need to make
sure google-service.json file is downloaded on each machine. Modify the cg-publish.py to point to the json
file location. 
  
Example workout publish calls:    
    
    #!/usr/bin/python3
    # Service to check permissions on Linux file
    import os
    import time
    
    def check_linux_perm():
        filename = '/usr/local/etc/protect_me/vulnerable.txt'
        status = os.stat(filename)
        permissions = oct(status.st_mode)[-3:]

        if permissions == '755':
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
            os.system('python3 /usr/local/bin/cg-publish.py missionpermissions-linux')   
        else:
          print('[!!] Files are still vulnerable!')
          time.sleep(180)
