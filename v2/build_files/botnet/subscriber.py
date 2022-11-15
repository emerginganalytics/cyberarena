from google.cloud import pubsub_v1
from concurrent.futures import TimeoutError
from attacks import *
import attack_manager
import cloud_env

__author__ = "Ryan Ronquillo"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Ryan Ronquillo"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Ryan Ronquillo"
__email__ = "rfronquillo@ualr.edu"
__status__ = "Testing"

class Subscriber:
    def __init__(self):
        self.env = CloudEnv()

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