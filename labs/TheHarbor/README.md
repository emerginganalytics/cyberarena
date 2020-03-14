# TheHarbor is a simple website that scans for open ports on click
There isn't a lot of configuration needed to run this site. 
```
[ System Requirements ]
	- Flask
	- Python 3.5 or later
	- Gunicorn
	- Nginx
	- Supervisor
	
Install with:
sudo apt-get install flask python3 gunicorn nginx-full supervisor
```   
Create a python3 virtual environment and with it activated install the requirements with ```pip3 install -r requirements.txt```   

I've opted to host this site on the same instance as PhishPhactor so just create a new nginx server block copying those settings.   
```
# [ /etc/nginx/sites-available/flask_settings ]
server {
	listen 3003;
	server_name 10.1.1.20;
	location / {
		proxy_pass http://0.0.0.0:5001;
		include proxy_params;
		proxy_set_header X-Real-IP $remote_addr;
	}
}
```   
Update NGINX: 
```
sudo ln -s /etc/nginx/sites-available/flask_settings /etc/nginx/sites-enabled/ 
sudo nginx -t
sudo nginx restart
```   

In ```/etc/supervisor/conf.d/```, create a file called ```theharbor.conf```. This is what we'll use to start TheHarbor on system boot. Replace the line ```/var/www/TheHarbor/fwenv/bin/gunicorn``` with the path to where gunicorn is installed in your virtualenv.   
```
# [ /etc/supervisor/conf.d/theharbor.conf ]
[program:theharbor]
directory=/var/www/TheHarbor/
command=/var/www/TheHarbor/fwenv/bin/gunicorn wsgi:application --bind localhost:5001 -w 3 --threads 16
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/gunicorn/TheHarbor.err.log
stdout_logfile=/var/log/gunicorn/TheHarobr.out.log

# [ eof ]
```   
Update supervisor: 
```
sudo supervisorctl reread
sudo supervisorctl update
```
