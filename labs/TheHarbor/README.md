# TheHarbor is a simple website that scans for open ports on click
There isn't a lot of configuration needed to run this site. 
```
[ System Requirements ]
	- Flask
	- Python 3.5 or later
	- Gunicorn
	- Nginx
	- Supervisor
```
I've opted to host this site on the same instance as PhishPhactor so just create a new nginx server block copying those settings.

In ```/etc/supervisor/conf.d/```, create a file called ```theharbor.conf```. This is what we'll use to start TheHarbor on system boot.
```
# [ /etc/supervisor/conf.d/theharbor.conf ]
[program:theharbor]
directory=/var/www/TheHarbor/
command=/usr/local/bin/gunicorn wsgi:application --bind localhost:5001 -w 3 --threads 16
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/gunicorn/TheHarbor.err.log
stdout_logfile=/var/log/gunicorn/TheHarobr.out.log

# [ eof ]
```
