# Assignment: Slowloris

This lab will introduce you to a few concepts that are important to cybersecurity professionals. You will learn how to create a website, how to verify the website is working, and how to perform the Slowloris attack. You will also learn how to secure your web server from such attacks.

***Note: It is important to know that performing a Slowloris attack is illegal and unethical. Knowledge about this attack should be used to protect your servers from such attacks instead.***

Slowloris is a type of attack that can cause a website or web server to stop working. It was created by Robert "RSnake" Hansen. The attack works by keeping many connections open to the target server for as long as possible. It does this by connecting to the server but only completing part of the request. Slowloris sends some information to the server but never finishes making the request. The server keeps these incomplete connections open, waiting for the request to be completed.

Slowloris keeps sending more information without completing the request, forcing the server to keep the connections open. This behavior eventually overwhelms the server's ability to handle new connections from legitimate users. The server has a limit on how many connections it can handle at once, and Slowloris uses up all those connections with its incomplete requests. This prevents legitimate users from connecting to the server and using it normally.

## Table of Contents

- [Assignment: Slowloris](#assignment-slowloris)
  - [Table of Contents](#table-of-contents)
  - [Lab Objectives](#lab-objectives)
  - [Deliverables](#deliverables)
  - [Rubric](#rubric)
  - [Creating Your Website](#creating-your-website)
  - [Part 1: Web Server Fundamentals](#part-1-web-server-fundamentals)
    - [Modifying a Web Server](#modifying-a-web-server)
  - [Accessing your Servers](#accessing-your-servers)
  - [Part 2: Attacking the Web Server](#part-2-attacking-the-web-server)
    - [Preparing the test command](#preparing-the-test-command)
    - [Running Slowloris](#running-slowloris)
  - [Part 3: Securing the Website](#part-3-securing-the-website)
    - [Option 1: Increase the number of connections](#option-1-increase-the-number-of-connections)
    - [Option 2: Limit the number of connections](#option-2-limit-the-number-of-connections)

## Lab Objectives

1. Slowloris is a type of attack that can cause a website or web server to stop working. It was created by Robert "RSnake" Hansen. The attack works by keeping many connections open to the target server for as long as possible. It does this by connecting to the server but only completing part of the request.
2. Slowloris sends some information to the server but never finishes making the request. The server keeps these incomplete connections open, waiting for the request to be completed. Slowloris keeps sending more information without completing the request, forcing the server to keep the connections open.
3. This behavior eventually overwhelms the server's ability to handle new connections from legitimate users. The server has a limit on how many connections it can handle at once, and Slowloris uses up all those connections with its incomplete requests. This prevents legitimate users from connecting to the server and using it normally.
4. It is important to know that performing a Slowloris attack is illegal and unethical. Knowledge about this attack should be used to protect your servers from such attacks instead.

## Deliverables

1. Build a Lab Report File with the following sections:
   - Title Page
     - Assignment name
     - Your Name
     - Professor Name
     - Date
   - Lab Observations
   - Lab Conclusion
   - Lab Reflection

2. Observations
   In the observation section, you will need to take screenshots of any step that is bolded in the instructions.
      - Please label the step with the step number and the step name.
      - Please label the screenshot with the step number and the step name.
      - screenshots should include your entire screen, nt just the workout area.
    **Example:**  
    Step 1 - Open the Chrome Browser ![Step 1 ](imgs/step1.jpg)
3. Conclusion
   In the conclusion, you will write a paragraph or two about what you learned in this lab. You should also include a paragraph about what you found interesting or challenging in this lab.

## Rubric

| Criteria | Exemplary (5) | Proficient (3) | Developing (1) | Score |
| -------- | ------------- | -------------- | -------------- | ----- |
| Lab Report File| Formatted perfectly Correctly, No major grammar/spelling errors| Minor errors with formatting, grammar \& spelling | Major errors with formatting, grammar \& spelling | 10% |
| Screenshots|All screenshots included| Missing 1-2 screenshots or not legible | Missing a majority of screenshots| 40% |
| Conclusion| Well thought out and researched, shows exemplary understanding of the lab | Shows understanding of lab | Does not comprehend lab assignment | 40% |

## Creating Your Website

In this first portion of the lab, you will create a website that you will later attack with Slowloris. You will use a web server that is already set up for you. You will also use a tool called WinSCP to transfer files between your lab environment and your computer.

## Part 1: Web Server Fundamentals

### Modifying a Web Server

To make your web server unique, you can create and upload your own webpage. Here is how you can do it:

1. **Locate the "data" folder on your desktop.**
2. **Find the "index" or "index.html" file in that folder.**
3. Right-click on the file and choose the option "Edit with Code" (or any text editor of your choice).
   Now, you will see the default webpage content. You can use this content or modify it to create your personalized webpage. If you need help producing creative ideas for your webpage, feel free to ask ChatGPT for suggestions.
   *TIP: To copy and paste between ChatGPT and your lab environment, you must click on the desktop in your browser and type Ctrl-Alt-Shift (or swipe for touch screen). This will open the clipboard shared between your lab and your computer. You can paste it inside the clipboard textbox. Then, when you click into the lab, you will be able to paste the clipboard's contents.*
4. **Test your site on the desktop by right-clicking anywhere in Visual Studio Code and selecting Show Preview.**
5. When finished, copy it to your web server by opening WinSCP in your tools folder on the Desktop.
   ![image](https://github.com/emerginganalytics/cyberarena/assets/71454038/8a0b442b-707e-4d96-aa23-af27fe6f4a7b)

## Accessing your Servers

1. **Log in to the "cyberarena@10.1.1.19" connection using the "Let's workout!" password. This will establish a secure connection between your desktop and the SSH web server, allowing file transfer.**
2. Once connected, you will see a split screen. You will see your desktop on the left side (with caps-lock). You will see your web server on the right side (with enter).
3. Double-click on the grey bar in the desktop section to open the `C:\Users\cyberarena\Desktop\data` folder. Double-click on the grey bar in the web server section and enter the directory `/var/www/html`.
   ![image](https://github.com/emerginganalytics/cyberarena/assets/71454038/a8271fb3-a304-4dc4-a77d-336848fcc7c3)
4. **Finally, copy over your index.html from the Desktop to the web server by dragging and dropping.**
5. The `/var/www/html`folder is the default location that content is served on your web server, and your web server will automatically look for an index.html file. You can check this by opening up a browser in the lab and navigating to `http://10.1.1.19`.
   *NOTE: Anyone else in the world can access your site by using the DNS name on your workout landing page.*

## Part 2: Attacking the Web Server

### Preparing the test command

By this point, you should have a PowerShell window by clicking on the arrow button next to the Chrome browser icon on the taskbar.

1. **Then run the following command:**

    ```powershell
    curl http://10.1.1.19
    ```

2. You should see the contents of your index.html file. If you do not, ask your instructor for help.
    ![image](https://github.com/emerginganalytics/cyberarena/assets/71454038/a5527e0b-cb77-4f10-a323-46d81758798f)

We will use this to test the Slowloris attack in a moment. Just keep the window open for now.

### Running Slowloris

To run Slowloris, go to your Tools folder and double-click on the PowerShell - Slowloris Directory shortcut file. Once PowerShell opens, you can run the following command:

1. **Run the following commands in the box below to start Slowloris.**

    ```Powershell
    Python slowloris.py 10.1.1.19
    ```

2. **This will start the Slowloris attack, and you can test this, but going to your curl PowerShell window, and rerunning the command to see if the page will load.**

    ![image](https://github.com/emerginganalytics/cyberarena/assets/71454038/5fb2cfed-40d3-4d95-9574-94e7f443fecc)

3. **You should be able to see that your website will quit loading during the attack.**
    *Note: If this does not work, you can use the command line `option -s` to increase the number of threads that will run against the web server.*

    ```powershell
    python slowloris.py -s 100
    ```

4. Stop the attack, type `Ctrl` + `C` or `⌘` + `C` 
    ***Note: You may have to type this twice.***


## Part 3: Securing the Website

To secure the website from a Slowloris attack, you have a few options.

1. Begin by opening an SSH session using the PuTTY client in your tools folder on the Desktop. 
2. Then, select the Web Server connection and click Open.
    ![image](https://github.com/emerginganalytics/cyberarena/assets/71454038/1f8fd374-ae38-4737-804d-6def49b1f7d2)
3. Use the following credentials.

    ```powershell
    Username: cyberarena
    Password: Let's workout!
    ```

    ***Note: You wil not be able to see the password as it is typed. This is normal.***

### Option 1: Increase the number of connections

Your first option is to set a timeout on incoming requests using the `mod_reqtimeout` module. If a request is not complete within the specified time, the module closes the connection. This helps to ensure that Slowloris cannot keep connections open indefinitely.

To add this setting perform the following on your open SSH PuTTY connection.

1. Edit the configuration file by typing:

    ```bash
    sudo vi /etc/httpd/conf/httpd.conf
    ```

2. **Scroll to the bottom of the file, and type the following:**

    ```vim
    <IfModule reqtimeout_module>
    RequestReadTimeout header=20-40,MinRate=500 body=20,MinRate=500
    </IfModule>
    ```

3. Hit your escape button and then type `:wq` which means write the file and quit vi. This will save the configuration file.  
    It should look something like this:

    ```vim
    <IfModule reqtimeout_module>
    RequestReadTimeout header=20-40,MinRate=500 body=20,MinRate=500
    </IfModule>
    ~
    ~
    ~
    :wq
    ```

4. Reload the web server by typing:

    ```bash
    sudo systemctl reload httpd
    ```

    ***Note: This should reduce the effect of Slowloris on your web server.***
5. **Re-run the Slowloris attack and see if it is still effective.**

### Option 2: Limit the number of connections

You can also edit the same httpd.conf file and limit the number of connections a client can claim.

To add this setting do the following on your open SSH PuTTY connection.

1. Edit the configuration file by typing:

    ```bash
    sudo vi /etc/httpd/conf/httpd.conf
    ```

2. **Scroll to the bottom of the file, and type the following:**

    ```vim
    <IfModule mod_limitipconn.c>
      <location />
    maxConnPerIP 1
      </location>
    </IfModule>
    ```

3. Hit your escape button and then type `:wq` which means write the file and quit vi. This will save the configuration file.  
    It should look something like this:

    ```vim
    <IfModule mod_limitipconn.c>
      <location />
    maxConnPerIP 1
      </location>
    </IfModule>
    ~
    ~
    ~
    :wq
    ```

4. Reload the web server by typing:

    ```bash
    sudo systemctl reload httpd
    ```
