# The PhishPhactor is a phishing website that works with Kali BeEF.
The goal of this workout is to demonstrate the danger of phishing attacks and a few ways to protect yourself from these attacks.
```
[ System requirements ]
Works best with Ubuntu 18.04 or later
	- Ruby, Ruby-dev
	- Gunicorn
	- NGINX
	- Flask
	- Python 3.5 or later
	- Supervisor
```
# Setup
First we can create a file in ```/etc/nginx/sites-enabled/``` and call it ```flask_settings```.

```
# NGINX Server Configuration
# [ PhishPhactor Ports ]

server {
	listen 3001;
	server_name <internal-ip>;
	
	location / {
		proxy_pass http://0.0.0.0:5000;
		proxy_set_header X-Real-IP $remote_addr;
		include proxy_params;
	}
  }

# [ BeEF ]
server {
	listen 3002;
	server_name <internal-ip>;

	location / {
		proxy_pass http://0.0.0.0:3000;
		proxy_set_header X-Real-IP $remote_addr;
		include proxy_params;
	}

 }

# [ eof ]
```
For Gunicorn to work, we need to establish an entry point called, wsgi.py.

```
# [ Gunicorn Entry Point // wsgi.py ]

from app import app as application

if __name__ == "__main__":
	application.run()


# [ eof ]
```
To make BeEF run on system boot / reboot we'll need to create two files.
In ```/usr/local/sbin/ ```, create a file called ```beef-startup.sh```.
``` 
# /usr/local/sbin/beef-startup.sh
# [ BeEF Startup Bash Script ]

#!/bin/sh
cd beef && sudo ./beef

# [ eof ]
```

Next, create the file called beef-startup.service in ```/etc/systemd/system/```. Reload systemd.

```
# /etc/systemd/system/beef-startup.service
# [BeEF Systemd Startup ]
[Unit]
Description=BeEF Startup on Boot

[Service]
ExecStart=/usr/local/sbin/beef-startup.sh

[Install]
WantedBy=multi-user.target

# [ eof ]
```
Finally we need to create a file called phishphactor.conf in ```/etc/supervisor/conf.d/``` to run PhishPhactor on system boot.
Once created, reload supervisor.
```
# /etc/supervisor/conf.d/phishphactor
[program:phishphactor]
directory=/var/www/PhishPhactor
command=/usr/local/bin/gunicorn wsgi:application --bind localhost:5000
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/gunicorn/PhishPhactor.err.log
stdout_logfile=/var/log/gunicorn/PhishPhactor.out.log

# [ eof ]
```
