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

Install with:	

sudo apt-get install ruby ruby-dev nginx python3-pip supervisor git
sudo git clone https://github.com/beefproject/beef
cd /beef && sudo ./install
```
[ NOTE ] Flask and Gunicorn can be installed in the virtualenv using ```pip3 install -r requirements.txt```   

# Setup
With the system requirements installed, we can now create a file in ```/etc/nginx/sites-enabled/``` and call it ```flask_settings```.

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
Update NGINX:   
```
sudo ln -s /etc/nginx/sites-available/flask_settings /etc/nginx/sites-enabled/
sudo nginx -t
sudo nginx restart
```   
For Gunicorn to work, we need to establish an entry point called, wsgi.py.

```
# [ Gunicorn Entry Point // wsgi.py ]

from app import app as application

if __name__ == "__main__":
	application.run()


# [ eof ]
```   
Update BeEF config.yaml with new username and password.   
Under the Reverse Proxy block, change the public address and port values to the values we set in the nginx server conf.   
Under the web_server_imitation block, change the type from apache to nginx.   

To make BeEF run on system boot / reboot we'll need to create two files.
In ```/usr/local/sbin/ ```, create a file called ```beef-startup.sh```.
``` 
# /usr/local/sbin/beef-startup.sh
# [ BeEF Startup Bash Script ]

#!/bin/sh
cd beef && sudo ./beef

# [ eof ]
```

Next, create the file called beef-startup.service in ```/etc/systemd/system/```.

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
Enable the service: ```sudo systemctl enable beef-startup.service```
Start the service: ```sudo systemctl start beef-startup.service```   

Finally we need to create a file called phishphactor.conf in ```/etc/supervisor/conf.d/``` to run PhishPhactor on system boot. Replace ```/var/www/PhishPhactor/phishenv``` with the path to your python3 virtual environment   
```
# /etc/supervisor/conf.d/phishphactor
[program:phishphactor]
directory=/var/www/PhishPhactor
command=/var/www/PhishPhactor/phishenv/bin/gunicorn wsgi:application --bind localhost:5000
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/gunicorn/PhishPhactor.err.log
stdout_logfile=/var/log/gunicorn/PhishPhactor.out.log

# [ eof ]
```   
Reload and update supervisor:   
```
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl status
```
