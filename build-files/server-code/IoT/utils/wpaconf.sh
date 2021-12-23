#!/bin/bash

cat << EOT > /etc/wpa_supplicant/wpa_supplicant.conf
ctrl_interface=/var/run/wpa_supplicant
update_config=1
country=US

network={
    ssid="uaca"
    scan_ssid=1
    psk="qxps7gmtv3"
}

network={
    ssid="NotWhoYouThink"
    psk="awesome3"
}
EOT
wpa_cli -i wlan0 reconfigure

cd /usr/src/cyberarena-dev
cp ./local/iot.pub /media/usb/
