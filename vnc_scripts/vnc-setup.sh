#!/bin/bash 
# startup script to setup vnc config used with tightvnc
# run as sudo

# Requirements for VNC server
echo "[*] Installing server requirements ..."
apt-get install gnome-core xfce4 tightvncserver -y

echo "[*] Configuring VNC server ..."
sudo tar -czvf vnc-servers.tar.gz /vnc-servers
sudo mv ./vnc-servers/cybergym1-vnc.service /etc/systemd/system/cybergym1-vnc.service
sudo mv ./vnc-servers/cybergym2-vnc.service /etc/systemd/system/cybergym1-vnc.service
sudo mv ./vnc-servers/cybergym3-vnc.service /etc/systemd/system/cybergym1-vnc.service
sudo mv ./vnc-servers/cybergym4-vnc.service /etc/systemd/system/cybergym1-vnc.service
sudo mv ./vnc-servers/cybergym5-vnc.service /etc/systemd/system/cybergym1-vnc.service

echo "[*] Initiating VNC Server ..."
sudo su cybergym1 -c "vncserver start :1"
sudo su cybergym1 -c "vncserver -kill :1"

sudo su cybergym2 -c "vncserver start :2"
sudo su cybergym2 -c "vncserver -kill :2"

sudo su cybergym3 -c "vncserver start :3"
sudo su cybergym3 -c "vncserver -kill :3"

sudo su cybergym4 -c "vncserver start :4"
sudo su cybergym4 -c "vncserver -kill :4"

sudo su cybergym5 -c "vncserver start :5"
sudo su cybergym5 -c "vncserver -kill :5"

echo "[*] Setting up xstartup files ..."
sudo cat /vnc-servers/xstartup > /home/cybergym1/.vnc/xstartup
sudo cat /vnc-servers/xstartup > /home/cybergym2/.vnc/xstartup
sudo cat /vnc-servers/xstartup > /home/cybergym3/.vnc/xstartup
sudo cat /vnc-servers/xstartup > /home/cybergym4/.vnc/xstartup
sudo cat /vnc-servers/xstartup > /home/cybergym5/.vnc/xstartup

echo "[+] Configuration complete ..."
echo "[+] If each user is configured properly: "
echo "[-->] Run sudo systemctl enable cybergym[1-5]-vnc.service && sudo systemctl start cybergym[1-5]-vnc.service"