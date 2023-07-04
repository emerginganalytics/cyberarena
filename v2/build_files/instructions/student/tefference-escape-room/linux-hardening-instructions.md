# Gigabyte APT
For this lab exercise, the cybersecurity response team has been notified that the **Advanced Persistent Threat (APT)** Gigabyte Group has infiltrated one of our machines.  This APT uses several known attack methods and vectors.  To successfully complete the lab, we’ll need to remove their access and properly harden the Linux system they compromised.

While the Gigabyte Group isn’t a real APT, [MITRE ATT&CK](https://attack.mitre.org) is an excellent resource for learning about real-world APTs and the **tactics, tools, and procedures (TTPs)** they use to compromise their targets.

For this lab, there are five known Gigabyte **indicators of compromise (IOCs)**.  Identify them and remediate any related vulnerabilities, footholds, and persistence mechanisms to complete the lab.

## Assignment
Review Gigabyte's Indicators of Compromise and perform the following tasks to secure the operating system. Your assignment will be automatically assessed after you complete each activity. It may take 1-2 minutes for the assessment to show up.
1. **Malicious User**: Delete the malicious user account
> **Hint:** run the command `cat /etc/passwd` to view all users on the system. The username is listed before the first colon. To delete the user, run `sudo deluser USERNAME` where USERNAME is replaced with the user you want to delete. When prompted for a password, use `Let's workout!`
3. **Privilege Escalation**: Remove the unnecessary privileges added by Gigabyte
4. **Malicious Files**: Delete the malicious files added by Gigabyte

# Gigabyte’s Indicators of Compromise
### Initial Access: Log4J Vulnerability
The Gigabyte Group is known for using the Log4j vulnerability to gain a foothold on its target systems.  What can you do to remediate this vulnerability and prevent further compromise?

### Persistence: New User Creation
After initial access, the Gigabyte Group will often create a new user account they can use to log back into and maintain access to the system using more conventional means.  Can you identify this account and remove it?

### Privilege Escalation: Valid Admin Account
Realizing that creating a new account may be an obvious red flag to system defenders, the Gigabyte Group will often attempt to compromise other legitimate accounts.  

It looks like the Group wasn’t able to compromise the root user, but they were able to compromise one of the legitimate accounts on the system and escalate its privileges.  Only the root user should have user-level assigned sudo privileges.  Can you verify no other accounts have these privileges?

### Persistence: Scheduled Task/Job
Gigabyte, like many other APTs, won’t give up its footholds easily. The Gigabyte will often use scheduled tasks or startup scripts to maintain persistent access to its targets.  Gigabyte is particularly fond of using crontab.  

Due to its complexity, defenders may overlook tasks meant to maintain persistence.  Can you identify the Gigabyte Group’s persistence mechanism on this machine?

### Impact: Pirated Video Placement
Finally, with its access secured, the Gigabyte Group likes to store pirated videos on target systems to blackmail its victims.  In our organization’s IT environment, video files, such as .wav and .mp4, are banned anyway.  Remove any of these from the system.

# Guide to the Linux Operating System {#linux-guide}
Linux is a computer **operating system (OS)** that is similar to other operating systems like Windows and macOS, but it is **free** and **open source.** This means that anyone can download and use Linux without having to pay for it. The source code of the operating system is freely available for anyone to modify and improve upon.

One of the most noticeable differences between Linux and other operating systems is the user interface. Linux offers a wide range of user interfaces, including desktop environments, that allow you to customize the look and feel of your system to your liking. Many Linux systems also operate without a desktop environment and instead rely on the **command line interface (CLI)**.

While Linux may take some time to learn for users who are used to other operating systems, it offers a lot of benefits for those who are willing to invest the time.

# Why is Linux Important in Cybersecurity?
Linux is important for cybersecurity professionals for several reasons:
Popularity
Linux is one of the most widely used operating systems in the world, especially in the server and cloud environments. This means that cybersecurity professionals must be familiar with Linux to secure these critical systems and infrastructure.

### Customizability
Linux is highly customizable, allowing users to configure it in ways that can enhance security. This can include configuring firewalls, installing intrusion detection systems, and hardening the system against attacks.

### Open Source
Linux is open source, which means that the source code is freely available for anyone to review and audit. This makes it easier to identify and fix vulnerabilities and also allows cybersecurity professionals to develop custom security tools and solutions.

### Command Line
The Linux command line provides powerful tools and utilities for managing the system, analyzing logs, and automating tasks. Many cybersecurity tools and scripts are designed to run on the Linux command line, so proficiency in this area is essential for cybersecurity professionals.

### Linux-based Tools
Linux is also commonly used in the field of penetration testing, which involves testing the security of systems by attempting to exploit vulnerabilities. Many of the tools used in cybersecurity for tasks like penetration testing and network defense are designed only to run on Linux.

# Navigating Linux
When you log into your lab environment, you’ll be presented with a desktop environment.  Open up the Linux command line by pressing the black box button at the bottom of your screen.

You’ll now be presented with a **terminal!**  Here, you can run commands that perform tasks on your computer.  Before we use some of those more advanced commands, let’s look at the Linux file system.

Linux’s file system, similar to Windows, is tree-like, but instead of beginning with a drive letter (`C:`), Linux begins at the root directory (`/`).  Everything else is an extension of the root directory, e.g. `/directory1/directory2/file.txt`.

See where you are in the Linux file system by running the command `pwd`, short for “print working directory.”  You can also see what user you’re logged in as using `whoami`.

The following section contains other useful Linux commands you can try out.

# Important Linux Commands
### `ls [/path/to/directory]`
Lists files and directories in the current directory. A different directory to list can also be specified as an argument.

The -l switch outputs the files and directories in a line-item list format.
The -a switch includes hidden files and directories.

### `cd [/path/to/directory]`
Changes the current directory.

Use `cd ~` to navigate to your home directory.
Use `cd -` to return to your last directory.
Use `cd ..` to navigate to your parent directory.

### `mkdir [directory name]`
Creates a new directory with the specified name.

### `rmdir [directory name]`
Deletes the directory with the specified name.

The -r switch will recursively delete all sub-files and sub-directories contained within the directory to be deleted.  Without this switch, rmdir only works on empty directories. 

### `rm [name]`
Removes the specified file(s) and/or directory(ies).  Use this command with caution!

### `mv [old path] [new path]`
Moves or renames the file stored at old_path.

### `cat [file]`
Displays the contents of the target file.

### `nano [file]`
Opens the nano text editor to create or edit a file.

### `vim [file]`
Opens the vim text editor to create or edit a file.

### `grep [pattern]`
Searches for the specified string or RegEx pattern in a file or files.


### `find [starting directory] [search pattern]`
Searches for files within the specified directory hierarchy.

The -type switch specifies whether to look for files or directories.
Use `find . -type f` to search for files.

The `find . -name *` switch specifies what file or directory names to look for.  A wildcard (*) can be used to specify multiple search patterns.

### `ping [target IP]`
Tests the network connectivity of the target system(s).

### `ssh [username]@[target IP]`
Securely connects to the specified account on a remote system.

### `history`
Shows a list of the previously executed commands.

### `echo [message]`
Prints a message to the terminal or a file.

### `touch [name]`
Creates a new empty file with the specified name.

### `pwd`
Print the current working directory.

### `sudo [command]`
Runs a command with elevated (root) privileges.

### `apt [command]`
Install, list, update, or remove software packages on Debian-based distributions.
