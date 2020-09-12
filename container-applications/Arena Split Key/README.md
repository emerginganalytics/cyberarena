# About   
This challenge exploits this vulnerability in [ProFTPd 1.3.5](https://www.exploit-db.com/exploits/36742) to gain access to another machine without possessing the password for that user.   

When a student successfully logs in via ssh to the user 'incatnito', a special 'message' will be displayed on the screen.

# Setup   
To set up this challenge, run the challenge_setup.sh with root priveleges. This will install all the needed dependencies as well as configure ProFTPd and the SMB server.    

Once the script is complete, you'll need to disable the default SFTP server.   
To do this:    

- Open ```/etc/ssh/sshd_config``` and comment out the following line: ```Subsystem sftp /usr/lib/openssh/sftp-server```.   
- Save and close the file
- Restart the sshd service.   

On older systems, the sshd service can be found in ```/etc/init.d/sshd```. Newer systems will have it running as a systemd service.   

Finally, you'll need to create a systemd service to maintain the ProFTPd server.    

- Move the proftpd.service file to ```/etc/systemd/system/``` directory.   
- Enable the service by calling: ```sudo systemctl enable proftpd.service```   
- Finally start the service with ```sudo systemctl start proftpd.service```   

### Changing the SSH Greeting   
If you want to change what message appears on the screen after a succesful SSH connection,  

- Open ```/usr/local/src/nyancat/src/nyancat.c``` and edit line 905 of the file.   
- Once the desired message is set, recompile the program by calling the *make* command in the ```/usr/local/src/nyancat/``` directory.   