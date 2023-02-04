import os
import requests
import sys

def updateDotEnv(token, workoutid, url):
    target_file = "/var/www/PhishPhactor/.env"
    with open(target_file, 'w') as f:
        f.write('TOKEN={}\n'.format(token))
        f.write('WORKOUT_ID={}\n'.format(workoutid))
        f.write('URL={}\n'.format(url))


def getEnv():
    TOKEN = os.environ.get('WORKOUTKEY0')
    WORKOUT_ID = os.environ.get('WORKOUTID')
    DNS_SUFFIX = os.environ.get('DNS_SUFFIX')
    URL = 'https://buildthewarrior{}/complete'.format(DNS_SUFFIX) 

    updateDotEnv(TOKEN, WORKOUT_ID, URL)

getEnv()