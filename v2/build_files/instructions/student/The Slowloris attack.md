# Table of Contents

## Lab Objectives

1. **Slowloris Attack**: Slowloris is a type of attack that disrupts websites or web servers. It keeps many connections open to the target server without completing requests, overwhelming its capacity to handle new connections and impacting legitimate users.

2. **Attack Mechanism**: Slowloris sends incomplete requests to the server, forcing it to keep connections open, eventually leading to a server overload.

3. **Impact on Servers**: This attack exhausts the server's connection limit, hindering regular users from accessing it.

4. **Ethical Consideration**: Note that performing a Slowloris attack is illegal and unethical. Knowledge of this attack should be used to defend servers against such attacks.

## Creating Your Website

To make your web server unique, follow these steps:

1. Locate the "data" folder on your desktop.
2. Find the "index" or "index.html" file in that folder.
3. Right-click the file and choose "Edit with Code" (or any text editor).
4. Modify the default webpage content or create your personalized webpage. ChatGPT can provide creative ideas.

TIP: To copy and paste between ChatGPT and your lab environment, use Ctrl-Alt-Shift (or swipe on touch screens) to access the shared clipboard.

5. Test your site by opening Visual Studio Code and selecting "Show Preview."

6. Copy your customized `index.html` to the web server using WinSCP in your "tools" folder.

## Accessing your Servers

1. Log in to the SSH webserver connection "cyberarena@10.1.1.19" using the password "Let's workout!" for secure file transfer.

2. In the split-screen interface, the left side represents your desktop and the right side represents the web server.

3. Double-click the grey bar in the desktop section to open the "C:\Users\cyberarena\Desktop\data" folder. Double-click the grey bar in the web server section to access "/var/www/html" directory.

4. Drag and drop your `index.html` from the Desktop to the web server.

5. Your web server will serve content from the `/var/www/html` folder, accessible at `http://10.1.1.19`.

## Attacking the Webserver

1. Prepare a PowerShell window by clicking the arrow button next to the Chrome browser icon on the taskbar.

2. Run the `curl` command to test website responsiveness.

3. Use the PowerShell window to run Slowloris attack. Open PowerShell and run the provided commands to start the attack.

4. Stop the attack with Ctrl+C (twice). Use the `-s` option to increase attack threads if needed.

5. To secure against Slowloris, set a timeout on incoming requests using the mod_reqtimeout module. Edit the configuration file, scroll to the bottom, and add the setting.

6. Reload the web server to apply changes.

7. Another option is to limit the number of client connections in the `httpd.conf` file.

Remember to use knowledge responsibly and ethically. Good luck!
