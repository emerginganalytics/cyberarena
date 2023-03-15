# SSH Keys Workout
Secure Shell (SSH) protocol is intended to provide system administrators access to servers (e.g., web servers, DNS servers, network devices, etc.). So, the credentials used to access the system must be protected at a high level. Many systems allow administrators to login with passwords, which have many weaknesses, including the propensity humans have for choosing weak passwords, sharing passwords, and being subject to type in passwords when prompted by a fake server.

As a result of these weaknesses, SSH access should be restricted to only allow access through asymmetric or public-key cryptosystems. In this lab, you will encounter an SSH login to a server configured for password authentication and apply the mitigation of RSA asymmetric key authentication. This is probably one of the more important skills system administrators and operators can learn to strongly secure their systems.

## Instructions
From the landing page, connect to the server where indicated to access your lab desktop environment. From here, open a new terminal window, and verify you can login to the following server:
```
ssh cyberarena@10.1.1.51
password: Let's workout
```
> :warning: **Blind password prompt**: The password will not be shown as you type.

Oh, no! You can login through SSH with only a password! Let's fix that. Use the following commands and configuration files to ensure login only occurs through asymmetric key authentication. You will need to explore the commands through a web search and figure out the precise commands to run. Once you have fully secured the login for the `cyberarena` user, then assessment will show complete.
* `ssh-keygen`: Run on your lab desktop machine to generate RSA public and private keys.
* `ssh-copy-id`: Use on your lab desktop to remotely copy your public key over to the remote server 10.1.1.51.
* `/etc/ssh/sshd_config`: Edit this file with nano or vim (e.g., `nano /etc/ssh/sshd_config`) to enforce asymmetric key authentication.
