# About   
This folder contains a series of useful Python and Bash scripts to help make the initial setup and maintainence the Iot device a little easier.   

## image_to_pixmap.py   

This script is designed to take the image directories specified in either the config.yaml or by argument, generate a pixel map from those images for the SenseHat.
With each directory provided, this script will write it out to a Python file in the form of a dictionary where each dir name is the key. 
While this could easily be done during runtime, processing large amount of images could create a heavy load.     

Currently, this function will overwrite any contents of the destination Python file. 

In order for this script to work, all files in the directory must be listed alphanumerically (*filename[1-N]*).   

Example:   
  - heart1.png
  - heart2.png
  - heart3.png
  - heart4.png

```
  ImageMaps = {
    'heart': [
      [
        [0, 0, 0], [0, 0, 0], [15, 15, 15], [0, 0, 0], [0, 0, 0], 
        [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [235, 17, 148], 
        [235, 17, 148], [15, 15, 15], [0, 0, 0], [235, 17, 148], 
        [235, 17, 148], [0, 0, 0], [235, 17, 148], [235, 17, 148], 
        [235, 17, 148], [235, 17, 148], [235, 17, 148], [235, 17, 148], 
        [235, 17, 148], [235, 17, 148], [235, 17, 148], [235, 17, 148], 
        [235, 17, 148], [235, 17, 148], [235, 17, 148], [235, 17, 148], 
        [235, 17, 148], [235, 17, 148], [0, 0, 0], [235, 17, 148], 
        [235, 17, 148], [235, 17, 148], [235, 17, 148], [235, 17, 148], 
        [235, 17, 148], [0, 0, 0], [0, 0, 0], [0, 0, 0], [235, 17, 148], 
        [235, 17, 148], [235, 17, 148], [235, 17, 148], [0, 0, 0], [0, 0, 0], 
        [0, 0, 0], [0, 0, 0], [0, 0, 0], [235, 17, 148], [235, 17, 148], 
        [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], 
        [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]
        ]],
```   

## checkState   

A simple bash script used to check and maintain SSH keys and Google's root.pem    

## iotctl.sh   

Allows you to quickly setup wireless networks, update and pull ssh keys, and check service and telemetry logs   
