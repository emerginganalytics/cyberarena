### This is a collection of scripts to help automate the setup of the vncservers.

#### [ Requirements: ]
  - Python3.5+
---

Download the vnc-servers.tar.gz file into the appropriate directory. 
 - cybergym[1-5]-vnc.service: This file goes in /etc/systemd/system/. This is how we run
      VNC as a service
 - vnc-setup.sh: Should install the appropriate dependencies and VNC client as well   
    as configures VNC for each CyberGym user.
    
 If everything was configured properly, you enable and start the service:
 ```
 sudo systemctl enable <cybergym[1-5]>-vnc.service
 sudo systemctl start <cybergym[1-5]>-vnc.service
 ```
 You can verify it started correctly by typing:
 ```
 sudo systemctl status <cybergym[1-5]>-vnc.service
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

Copy the contents of the xstartup file into each respective ~/.vnc/xstartup file.
```
sudo cat xstartup > /home/<cybergym1-5>/.vnc/xstartup
```   
# [ !!IMPORTANT!! ] You need to update Labentry for each new VNC server created!   
Log into the guac server, go to settings > connections > add connection or you can click on an existing connection, clone it, and change the IP and port numbers to match the new server internal ip.   

Once you have that configured, you need to go to the **user** tab and click on each user and give them rights to access the new connection.   
Save and re-image Labentry.
