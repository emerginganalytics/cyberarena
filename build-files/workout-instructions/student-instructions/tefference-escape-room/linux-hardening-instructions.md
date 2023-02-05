# Linux Hardening Instructions
Welcome to the puzzle for hardening a linux server. In this puzzle, you'll need to review Linux Ubuntu 18 settings and fix insecure configurations. Once you fix the problems, the puzzle will reveal a clue automatically within about a minute after completion.

## Instructions
* A terminal should be up when you initially login. Type in ssh cyberarena@10.1.1.51. Accept the ssh key warning and then type in the password `Let’s workout!`
* Run through the settings to identify the insecure configurations.
> **_HINT:_** Run through the commands below to find anything suspicious, and then search online for ways to fix the problem.

## Helpful commands to harden Linux
* Software Management
  * `apt list --installed`: Shows the software installed on the server
* Network Services
  * `sudo lsof -i -n -P | more`: Explore network services
* Users
  * `less /etc/passwd`: Lists users on the server
* Listing services
  * `systemctl list-units --type=service`: Lists running services on the server.
