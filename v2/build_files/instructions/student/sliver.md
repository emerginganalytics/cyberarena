# Sliver Botnet Instructions

## Accessing your Servers
The Sliver controller server is called Sliver Server. Right now, it's best to open this in an incognito browser to avoid caching the credentials used to connect.
![image](https://user-images.githubusercontent.com/50633591/234986130-619d61f1-1a5b-47e7-9efa-555311ccb725.png)

When you are ready to connect to your implant server, make sure to close your Sliver server first, and then you can connect incognito in the same way.

## Sharing your Implants
When you create your implants, move them to the `/src/sliver` folder on the Sliver server. Then, they can be accessed by other Windows servers in the lab. To have someone else run your implant, send them the IP address of the Sliver Server (e.g. 10.1.0.XX). Then, they can run your implant by going to their implant server, and opening explorer. From explorer, they can double click on the executable in the Sliver folder.

![image](https://user-images.githubusercontent.com/50633591/234988380-81fc9370-148b-4c2c-a816-7b1b14ba47de.png)
