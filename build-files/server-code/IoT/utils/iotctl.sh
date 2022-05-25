#!/bin/bash
# This script is intended to make general maintainence for the Pi SenseHat service a little easier.
# Current functionality includes, updating ssh keys, checking service status, logs, updating system
# wpa file
#
# Author: Andrew Bomberger
# For: UA Little Rock Cyber Arena

iot_home='/usr/src/cyberarena-dev'
external_drive='/media/usb'
ext_code="$external_drive/iot-code"
wpa_file="$iot_home/local/wpa_supplicant.conf"

function usage(){
	cat <<USAGE
	Usage: iotctl [-k keys] [-l logs] [-s status] [-u update] [-w wpa] [-h help]
	
	Options:
		-k, --update-ssh: Updates SSH keys and copies to mounted /media/usb
		-l, --logs: Checks Telemetry logs
		-s, --status: Checks sensehat.service status
		-u, --update-code: Copies code stored in /media/usb/iot-code to /usr/src/cyberarena-dev/*
		-w, --update-wpa: Updates wpa_supplicant file with whatever values are stored in current file
		-h, --help
USAGE
	exit 1
}
function restart() {
	# Restart SenseHat Service to See Changes
	systemctl restart sensehat.service
}
function update_wpa(){
	echo "[+] Updating wpa_supplicant"
	if [ ! -d $wpa_file ]; then
	       echo "[!!] $wpa_file does not exist. Exiting ..."
	       exit 1
 	fi		
	echo "[*] Appending $wpa_file to /etc/wpa_supplicant.conf"
	cat $wpa_file >> /etc/wpa_supplicant.conf
	
	wpa_cli -i wlan0 reconfigure
	ifconfig
	# Restart sensehat service
	restart
}
function update_code(){
	# Copy code on ext drive to development directory
	if [ -d /media/usb ]; then
		cp -R $ext_code/* $iot_home	
	fi
	
	echo "[+] Updating System Aliases ..."
	echo "alias iotctl='/usr/src/cyberarena-dev/utils/iotctl.sh" >> ~/.bash_aliases
	echo "alias iotdev='cd /usr/src/cyberarena-dev'" >> ~/.bash_aliases
	
	# Reload bashrc
	source ~/.bashrc
	# Restart sensehat service
	restart	
}
function status() {
	# Check SenseHat service status
	systemctl status sensehat.service
}
function check_logs(){
	# Check Telemety Logs
	tail $iot_home/telemetry.log
	echo " "
	echo "To view all telemetry logs, see $iot_home/telemetry.log"
}
function update_ssh() {
	# Update SSH Keys
	rm -rf /usr/src/cyberarena-dev/local/iot.pub
	echo "[+] Regenerating Keys ..."
	./usr/src/cyberarena-dev/checkState
	echo "[+] Copying new public key to mounted drive ..."
	cp /usr/src/cyberarena-dev/local/iot.pub /media/usb
}

# Force run as sudo/root
if [[ $EUID -ne 0 ]]; then
	echo "[!!] $0 is not running as root. Exiting ..."
	exit
fi
# Check for arguments
if [ $# -eq 0 ]; then
	usage
	exit 1
fi
# Get flags from script call
for arg in "$@"; do
	case $arg in 
		-k | --update-ssh) update_ssh;;
		-l | --logs) check_logs;;
		-s | --status) status;;
		-u | --update-code) update_code;;
		-w | --update-wpa) update_wpa;;
		-h | --help) usage;;
		*) usage;; # wrong arg provided print usage
	esac
done
