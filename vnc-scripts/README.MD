# VNC Server Configuration Scripts
---
---
#### This collection of scripts is used to speed up the process of installing and configuring a VNC server with support of multiple connections per user.   

### [ How this works ]

Pull and extract the contents of the vnc_scripts.zip into the desired location.   
Modify the file vncservers.conf to meet the needs of the current instance.
##### [ EXAMPLE ]: 
      VNCSERVERS="1:user1 2:user2 3:user3
      VNCSERVERARGS[1]="-geometry 800x600 -depth 8"
Make vnc-setup.sh executable and then run it.
Once the script finishes, you'll need to login as each user and type `vncserver` to initialize the server for that user.   
Once the server starts for that user, you can  run `sudo cat vnc-xstartup.txt > ~/.vnc/xstartup`   
Repeat for all desired users.
Finally, you can enable the service to run at system start by typing:
```
sudo update-rc.d vncserver defualts 99
sudo /etc/init.d/vncserver start
```

#### [ Optional ]:
Run the set_wallpaper.sh script to copy the wallpaper to each user's directory. Login through VNC and change the wallpaper
