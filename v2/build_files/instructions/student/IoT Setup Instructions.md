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
![RaspberryPi](https://github.com/emerginganalytics/cyberarena/assets/50710945/354b8553-e0ec-427d-a5dd-77b85dd50e72)

## Sense HAT
![SenseHat](https://github.com/emerginganalytics/cyberarena/assets/50710945/6d432937-83ad-4c7b-b7e4-f020e7527afc)


**Step 2:** Assemble the Raspberry Pi inside the provided case. Ensure that the metal Raspberry Pi pins are exposed through the lid of the case. Then, connect the Sense HAT to the Raspberry Pi by ***carefully*** plugging the pins into the black HAT header. 

When assembled, the Raspberry Pi should look like the following image.
![Assembled](https://github.com/emerginganalytics/cyberarena/assets/50710945/235313e4-2e91-441e-9a47-61776a21e40e)

**Step 3:** Connect the HDMI cable, USB hub, and power supply to the Raspberry Pi. The ports can be found from left to right looking at the side of the case.
![RPIPorts](https://github.com/emerginganalytics/cyberarena/assets/50710945/2eebc0b9-2a2d-49d7-a4f0-d117e8656daf)

**Step 4:** Plug the keyboard’s Bluetooth adapter to the USB hub. The adapter can be found inside the battery compartment of the keyboard.

**Step 5:** Connect the HDMI cable to a monitor and power on. It will take a few minutes to boot up. 

**Step 6:** When prompted for the username and password, use your keyboard to type: 

- Username: pi 

- Password: R3pr3$ent! 

**Step 7:** Run `sudo raspi-config` to configure wireless. You’ll see a screen  similar to the one below 
![IMG_20230616_100313](https://github.com/emerginganalytics/cyberarena/assets/50710945/6e77f521-3801-47be-b498-9ca7c49694c3)

**Step 8:** Select System Options > Wireless LAN, and enter the wireless network  name and password for your home wireless network. 

**Step 9:** Restart your Raspberry Pi with sudo reboot. If the device makes a  successful connection, you should see a rotating image display on your device  screen.
 
**Step 10:** Go to https://gencyber-classified.test-cybergym.org/iot/. Enter the  name of the device (e.g. cyber-arena-001) on the bottom of your Raspberry Pi  case. Then try sending a couple of commands to the device. If the device does not  work, then please email cybergym@ualr.edu and include the device ID to let us  know.
