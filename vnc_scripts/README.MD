# VNC Scripts:   

---   
### This is a collection of scripts to help automate the setup of the vncservers.

#### [ Requirements: ]
  - Python3.5+
---

Download the vncserver.zip file into the appropriate directory. 
 - vncserver.py: Is what starts the servers for CyberGym users 1-5
 - vncserver.service: This file goes in /etc/systemd/system/. This is how we run
      the script as a service
 - vnc-setup.sh: Should install the appropriate dependencies and VNC client as well   
    as configures each CyberGym user.
    
 If everything was configured properly, you enable and start the service:
 ```
 sudo systemctl enable vncserver.service
 sudo systemctl start vncserver.service
 ```
 You can verify it started correctly by typing:
 ```
 sudo systemctl status vncserver.service
 ```
 
 
### If you run into issues with the vnc-setup, you can always set up each user manually with the following:

With the above files in the appropriate directories, run the following two  
commands as each CyberGym(1-5) user:   
```
su <username> -c "vncserver start :<display>"
su <username> -c "vncserver -kill :<display>"
```   
This will initiate the server and establish a password for each connection. The last command
kills the connection to ensure there won't be any errors when starting the service.   

Copy the contents of xstartup.txt into each respective ~/.vnc/xstartup file.
```
sudo cat xstartup.txt > /home/<cybergym1-5>/.vnc/xstartup
```   
