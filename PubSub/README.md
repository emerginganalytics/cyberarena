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
## [ cg-publish.py ]:   
This script can be used with any workout. In order for the script to work properly, you'll need to make
sure google-service.json file is downloaded on each machine. Modify the cg-publish.py to point to the json
file location. 
  
Example workout publish calls:    

    #!/usr/bin/python3
    import os
    import socket
    import logging

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

    def check_win_perm():
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('10.128.0.20', 5555))
        s.listen(5)

        conn, addr = s.accept()
        data = conn.recv(1024).decode('utf-8')

        if data:
            print('[+] Message Received: {}'.format(data))
            s.close()
            return True

    # if workout is complete, publish
    check_linux = check_linux_perm()
    check_windows = check_win_perm()

    if check_linux and check_windows:
        print('[*] Publishing Results ...')
        os.system('python3 /usr/local/bin/cg-post.py permissions')   

