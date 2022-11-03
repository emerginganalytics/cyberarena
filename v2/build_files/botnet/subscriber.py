import os
import subprocess
from google.cloud import pubsub_v1
from concurrent.futures import TimeoutError
from google.cloud import runtimeconfig
from attacks import *
import attack_manager

class Subscriber:
    def __init__(self):
        runtimeconfig_client = runtimeconfig.Client()
        myconfig = runtimeconfig_client.config('cybergym')
        self.project = myconfig.get_variable('project').value.decode('utf-8')
        self.region = myconfig.get_variable('region').value.decode('utf-8')
        self.zone = myconfig.get_variable('zone').value.decode('utf-8')
        self.dns_suffix = myconfig.get_variable('dns_suffix').value.decode('utf-8')

creds = '/home/walker/Downloads/ualr-cybersecurity-38b2dd265fa9.json'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = creds

timeout = 5.0

subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path('ualr-cybersecurity', 'test-sub')

def callback(message):
    print(f'Received message: {message}')
    print(f'data:{message.data}')
    message.ack()

streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
print(f'Listening for messages on {subscription_path}')

with subscriber:
    try:
        streaming_pull_future.result()
    except TimeoutError:
        streaming_pull_future.cancel()
        streaming_pull_future.result()
