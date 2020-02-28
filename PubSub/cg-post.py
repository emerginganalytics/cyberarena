#!/usr/bin/python3
from google.cloud import pubsub_v1

import base64 as b64
import os
import requests
import sys

# NOTE change environment = .json system location
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '<json file location>'

# parsing hostname to determine workout_ID and team number; type=sys.arv[1]
name = os.uname()[1]
data = name.split("-")

w_id = data[0]
w_type = sys.argv[1]
team_num = data[-1]

w_string = '{}-{} workout: complete!'.format(w_type, team_num)
message = b64.b64encode(w_string.encode('utf-8'))

# create publish session and publish message
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path('ualr-cybersecurity', \
        '{}-{}-{}-workout'.format(w_id, w_type, team_num))

# error handling
def get_callback(future, data):
    def callback(future):
        try:
            print(future.result())
        except: # noqa
            print("Please handle {} for {}.".format(future.exception(), data))
    return callback

future = publisher.publish(topic_path, data=message)
future.add_done_callback(get_callback(future, message))

# test values
print('[*] Publishing workout status ...')
print('[*] message: {}'.format(message))
