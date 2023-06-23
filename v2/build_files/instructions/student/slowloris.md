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




