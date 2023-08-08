# What is SSH:

Secure Shell (SSH) is a way for system administrators to connect to and control servers, such as websites, online databases, and other devices, over the internet. The login information must be protected well to ensure secure connections. While passwords are commonly used for login, they have various security issues. People often choose easily guessable passwords, share them, or fall for phishing attacks on fake websites.

To enhance SSH security, asymmetric or public-key systems are recommended. This involves using a unique digital key, like an RSA key, that only the authorized person possesses. In this lab, you'll learn how to utilize the RSA key to log in to a server, improving security and benefiting system administrators in protecting their systems.

## Examples:

1. **Website Administration**: Imagine you own a website and want only authorized individuals to make changes. SSH with an RSA key allows you to grant access exclusively to these authorized users.

2. **Remote Device Control**: Suppose you need to remotely manage a network device (e.g., a router). By utilizing SSH with a unique key, you can securely control the device without concerns of unauthorized access.

## SSH Instructions:

1. Connect to the server indicated on the landing page to access your lab desktop environment. Open a new terminal window from here and verify your ability to log in to the specified server.
2. ssh cyberarena@10.1.1.51
3. password: Let's workout !

   > **Note**: The password you type into the terminal will not be displayed.

4. To enhance security, the transition from password-based login to asymmetric key authentication using the following commands and configuration files:

   - Run `ssh-keygen` on your lab desktop machine to generate RSA public and private keys.

   - Use `ssh-copy-id` on your lab desktop to remotely copy your public key to the remote server located at IP address 10.1.1.51.

   - Edit the `/etc/ssh/sshd_config` file with `nano` or `vim` (e.g., `nano /etc/ssh/sshd_config`) to enforce asymmetric key authentication.

   Once you've completed these steps and secured the login for the user 'cyberarena', the assessment will show as complete.
