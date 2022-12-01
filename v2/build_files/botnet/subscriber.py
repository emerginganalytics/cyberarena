from google.cloud import pubsub_v1
from concurrent.futures import TimeoutError
from attacks import *
from attack_manager import *
from cloud_env import *

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
        self.timeout = 5.0
        self.subscriber = pubsub_v1.SubscriberClient()
        self.subscription_path = self.subscriber.subscription_path(self.env.project, self.env.agent_subscription)

    def callback(self, message):
        print(f'Received message: {message}')
        print(f'data:{message.data}')
        message.ack()
        if message.attributes.build_id == self.env.build_id:
            AttackManager(message.attributes).parse_message()

    def run(self):
        streaming_pull_future = self.subscriber.subscribe(self.subscription_path, callback=self.callback)
        print(f'Listening for messages on {self.subscription_path}')

        with self.subscriber:
            try:
                streaming_pull_future.result()
            except TimeoutError:
                streaming_pull_future.cancel()
                streaming_pull_future.result()

if __name__ == '__main__':
    Subscriber().run()