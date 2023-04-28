# Sliver Botnet Instructions

## Accessing your Servers
You have 3 servers in your lab:
* **sliver-server**: Ubuntu server with the role of command and control of the botnet.
* **sliver-client**: Used to control the C2 server
* **sliver-implant**: A test victim server used for installing implants.

>! **Warning:** When connecting to servers, it is best to open this in an incognito browser to avoid caching the credentials used to connect. Only connect to one of the servers at a time, and then, only in incognito mode.

![image](https://user-images.githubusercontent.com/50633591/234986130-619d61f1-1a5b-47e7-9efa-555311ccb725.png)

## Sharing your Implants
When you create your implants, move them to the `/src/sliver` folder on the Sliver server. Then, they can be accessed by other Windows servers in the lab. To have someone else run your implant, send them the IP address of the Sliver Server (e.g. 10.1.0.XX). Then, they can run your implant by going to their implant server, and opening explorer. From explorer, they can double click on the executable in the Sliver folder.

![image](https://user-images.githubusercontent.com/50633591/234988380-81fc9370-148b-4c2c-a816-7b1b14ba47de.png)
