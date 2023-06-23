> **Disclaimer:** The purpose of the lab environment is solely for educational and research purposes within the context of authorized and supervised activities. This lab environment is established to facilitate learning, analysis, and understanding of malware and related cybersecurity concepts. The malware lab environment is equipped with security measures to prevent unauthorized access and the spread of malware. However, it is essential to exercise caution and follow established protocols to minimize the risk of accidental exposure, infection, or unintended distribution of malware.

# The Slowloris Attack
Slowloris is a type of Denial of Service (DoS) attack that Robert "RSnake" Hansen invented. This attack works by holding as many connections open to the target web server for as long as possible. It accomplishes this by creating connections to the target server but only sending a partial request.

Slowloris sends HTTP headers to the target server but never completes a request. The server keeps these false connections open, waiting for each request to be completed. However, Slowloris continuously sends more HTTP headers but never completes a request. The server, waiting for the requests to be finished before closing the connection, is forced to maintain these false connections open.

This behavior eventually overwhelms the maximum concurrent connection pool of the server and leads to denial of service as new connections (from legitimate users) cannot be created. This attack is particularly effective against multi-threaded servers, where each connection requires a separate thread, and thus, the maximum number of connections can be quickly reached and tied up with slowloris connections.

It's important to note that conducting a Slowloris attack is illegal and unethical. Knowledge about this attack should be used to defend your servers against such an attack.

## Creating your website
Your webserver has only the default website from Apache Tomcat. Customize it by creating your own `index.html` file and uploading it to the server. To do so, follow these steps:
1. Open your **data** folder on the desktop. Then right-click on index (or index.html) and click _edit with Code_
2. Here you will see a default webpage. You can use this or customize it to make your own web page. Feel free to ask ChatGPT to come up with some sort of creative webpage.
> **TIP:** To copy and paste between ChatGPT and your lab environment, you must click on the desktop in your browser and type Ctrl-Alt-Shift (or swipe for touch screen). This will open the clipboard shared between your lab and your computer. You can paste it inside the clipboard textbox. Then, when you click into the lab, you will be able to paste the contents of the clipboard.
3. Test your site on the desktop by right clicking anywhere in Visual Studio Code, and select _Show Preview_
4. When you have finished, copy it over to your webserver by opening WinSCP in your **tools** folder on the Desktop.
![image](https://github.com/emerginganalytics/cyberarena/assets/50633591/d45a1ccc-f43b-4133-a1c9-e7aceadbc5d7)
5. Click login to the cyberarena@10.1.1.19 connection and use the password `Let's workout!`. This will connect to your web server and securely transfer files between your desktop and the SSH webserver.
6. You will then see a split screen. On your left-side (the side with caps-lock on your keyboard), you will see your desktop, and on your right side (the side with enter on your keyboard), you will see your web server.
7. For your desktop, double click on the grey bar to open the `C:\Users\cyberarena\Desktop\data` folder. Then, for your web server, double click on the grey bar and type in the directory `/var/www/html`
![image](https://github.com/emerginganalytics/cyberarena/assets/50633591/7f6406a9-a814-41ad-a0f3-cbb304f88024)
8. Finally, copy over your index.html from the Desktop to the web server by dragging and dropping.
9. The `/var/www/html` folder is the default location that content is served on your web server, and your web server will automatically look for an index.html file. You can check this by opening up a browser in the lab, and navigating to http://10.1.1.19.
> **NOTE:** Anyone else in the world can access your site by using the DNS name on your workout landing page.

## Attacking the webserver
### Preparing the test command
Before you start the slowloris attack, open up a Powershell window by clicking on the arrow button next to the Chrome browser icon on the taskbar. Then run the following command in Powershell:
```
curl http://10.1.1.19
```
The `curl` (client URL) command is like opening the website in your browser, but it allows us to have instant feedback to know if the website is responding. When you run the command, you should see something like the following:
![image](https://github.com/emerginganalytics/cyberarena/assets/50633591/472d3af2-33d2-48f2-8023-db809acac032)
We'll use this to test the slowloris attack in a moment. Just keep the window open for now.

### Running Slowloris
To run slowloris, go to your Tools folder, and double click on the `Powershell - Slowloris Directory` shortcut file. Once Powershell opens, you can run the following command:
```
python slowloris.py 10.1.1.19
```
This will start the Slowloris attack, and you can test this, but going to your `curl` Powershell window, and rerunning the command to see if the page will load.
![image](https://github.com/emerginganalytics/cyberarena/assets/50633591/4f661c05-f5f4-48ed-9daf-98a64fb69673)
To stop the attack, type Ctrl+C (you may have to type this twice).
You should be able to see that your website will quit loading during the attack. If this does not work, you can use the command line option `-s` to increase the number of threads that will run against the webserver.

You can show this to your instructor by asking them to pull the website on their computer and browse to the DNS that you have listed on your workout landing page.

## Securing the website
To secure the website from a slowloris attack, you have a few options. Begin by opening up an SSH session using the PuTTY client in your **tools** folder on the Desktop. Then, select the Web Server connection and click Open.

![image](https://github.com/emerginganalytics/cyberarena/assets/50633591/c8ff920c-918b-4eec-bc96-9895dc8c2692)

Use the following credentials:
```
User: cyberarena
Password: Let's workout!
```
> **NOTE:** This is a blind password prompt. You will not see the password as it's being typed.

Your first option is to set a timeout on incoming requests using the mod_reqtimeout module. If a request doesn't complete within the specified time, the module closes the connection. This helps to ensure that Slowloris can't keep connections open indefinitely. To add this setting perform the following on your open SSH PuTTY connection.
1. Edit the configuration file by typing:
```
sudo vi /etc/httpd/conf/httpd.conf`
```
2. Scroll to the bottom of the file, and type the following:
```
<IfModule reqtimeout_module>
  RequestReadTimeout header=20-40,MinRate=500 body=20,MinRate=500
</IfModule>
```
3. Type escape and then `:wq` (which means write the file and quit vi). This will save the configuration file.
4. Reload the web server by typing:
```
sudo systemctl reload httpd
```
This should reduce the effect of slowloris on your web server. You can also edit the same httpd.conf file and limit the number of connections a client can claim. To do so, you would, again, scroll to the bottom of the file and add the configuration:
```
<IfModule mod_limitipconn.c>
    <Location />
        MaxConnPerIP 1
    </Location>
</IfModule>
```
And then, don't forget to reload httpd.
