#!/usr/bin/python3
import os
import requests
import sys

# TODO REMOVE THIS COMMENT BLOCK ONCE ADDED TO EACH VM
# This script is built soley for the purpose of posting to CyberGym
# endpoint as a workout completion checkpoint. 
# Validation scripts will check the appropriate workout conditions
# and call this funtion when done. Example call: os.system('python cg-post.py')

# parsing hostname to determine workout_ID, type, and team number
name = os.uname()[1]
data = name.split("-")

w_id = data[0]
w_type = data[1] 
team_num = data[-1]

# TODO Add CyberGYm endpoint URL for Pub/Sbu
URL = "http://localhost"

data = {
        'workout_ID':w_id,
        'team_num': team_num,
        'status':'Q29tcGxldGUh',
        }
print('[*] Posting Workout Status ...')
r = requests.post(url=URL, data=data)

# [eof]
