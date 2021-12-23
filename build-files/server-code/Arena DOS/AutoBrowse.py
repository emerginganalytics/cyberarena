"""
    Prog       : AutoBrowse.py
    Created by : FUT1LE
    Created For: UA Little Rock Cyber Gym
    Date       : 11/23/2020

    Purpose    : Used for creation of pcap files.
                 simulates generic web traffic for 
                 set amount of time (end_time variable).
"""
import requests
from random import randint
from time import sleep, time

end_time = time() + 60 * 15
links = [
    "https://espn.com",
    'https://google.com',
    'https://yahoo.com',
    'https://github.com',
    'https://www.youtube.com/hak5',
    'https://www.hackthebox.eu/individuals',
    'https://cyberskyline.com/hosted_events',
    'https://tryhackme.com/hacktivities',
    'https://gmail.com',
    'https://www.bungie.net/',
]

while time() < end_time:
    # Loop runs and generates traffic for 15 minutes
    rand_pos = randint(0, len(links) - 1)
    sleep_len = randint(0, 30)
    
    request = requests.get(links[rand_pos]).status_code
    
    print(f'Result : {links[rand_pos]} : {request}')
    print(f'[+] Sleeping for {sleep_len}s')
    sleep(sleep_len)
