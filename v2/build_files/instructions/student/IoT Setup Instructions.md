# NSA GenCyber IoT Device Instructions 

Your Raspberry Pi Zero device is configured to work with the UA Little Rock Cyber  Arena. Follow these instructions to configure this device to work on your home  network: 

Step 1: Unpack everything and make sure you have the following materials.
RPI Zero with Sense HAT

## Power Supply
![image](https://github.com/emerginganalytics/cyberarena/assets/122807407/e0698598-c265-471d-8da2-0cb94c04e21d)

## HDMI Cable
![image](https://github.com/emerginganalytics/cyberarena/assets/122807407/69fcdeb0-3c5a-4199-b258-006d296cd9b6)

## USB Hub
![image](https://github.com/emerginganalytics/cyberarena/assets/122807407/b182b180-1ef3-4fa6-9c8d-e168ec018303)

## Keyboard
![image](https://github.com/emerginganalytics/cyberarena/assets/122807407/c7092755-2cdb-4099-97d9-0fa6a0fdf31b)

## Raspberry Pi
![image](https://github.com/emerginganalytics/cyberarena/assets/122807407/e64afec1-64d1-4ad2-95a2-666b149b0a53)

## Raspberry Pi Case
![image](https://github.com/emerginganalytics/cyberarena/assets/122807407/afde5284-c361-4df9-9d06-1b8fb645fd64)

## Raspberry Pi Micro SD Card and Adapter
![image](https://github.com/emerginganalytics/cyberarena/assets/122807407/59193eba-ba15-4f05-81fd-3d05bf6a1894)

**Step 2:** Assemble the Raspberry Pi inside the provided case. Ensure that the metal Raspberry Pi pins are exposed through the lid of the case. Then, connect the Sense HAT to the Raspberry Pi by plugging the pins into the black HAT header.

**Step 3:** Place the MicroSD card in its adapter.

**Step 4:** Connect the HDMI cable, USB hub, and power supply to the Raspberry Pi.

**Step 5:** Plug the keyboard’s Bluetooth adapter to the USB hub. 

**Step 6:** Connect the HDMI cable to a monitor. It will take a few minutes to boot up,  and then prompted for the username and password, use your keyboard to type: 

Username: pi 

Password: R3pr3$ent! 

**Step 7:** Run `sudo raspi-config` to configure wireless. You’ll see a screen  similar to the one below 
![image](https://github.com/emerginganalytics/cyberarena/assets/122807407/cabefae1-b3ff-4c3d-825c-914c0f69e3ec)

**Step 8:** Select System Options > Wireless LAN, and enter the wireless network  name and password for your home wireless network. 

**Step 9:** Restart your Raspberry Pi with sudo reboot. If the device makes a  successful connection, you should see a rotating image display on your device  screen.
 
**Step 10:** Go to https://cybergym-classified.cybergym-eac-ualr.org/iot/. Enter the  name of the device (e.g. cyber-arena-0001) on the bottom of your Raspberry Pi  case. Then try sending a couple of commands to the device. If the device does not  work, then please email cybergym@ualr.edu and include the device ID to let us  know.
