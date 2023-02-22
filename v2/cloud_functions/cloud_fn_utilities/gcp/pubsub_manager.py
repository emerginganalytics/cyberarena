import time
import googleapiclient.discovery
import logging
from google.cloud import logging_v2
from google.cloud import pubsub_v1
from googleapiclient.errors import HttpError
from google.api_core.exceptions import AlreadyExists, NotFound

from cloud_fn_utilities.gcp.cloud_env import CloudEnv

__author__ = "Philip Huff"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff", "Andrew Bomberger"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class PubSubManager:
    def __init__(self, topic, env_dict=None):
        self.env = CloudEnv(env_dict=env_dict)
        log_client = logging_v2.Client()
        log_client.setup_logging()
        self.publisher = pubsub_v1.PublisherClient()
        self.subscriber = pubsub_v1.SubscriberClient()
        self.topic_path = self.publisher.topic_path(self.env.project, topic)

    def create_topic(self):
        try:
            response = self.publisher.create_topic(request={"name": self.topic_path})
            logging.info(f'Created topic:\n{response}')
        except AlreadyExists:
            logging.warning(f'Topic with {self.topic_path} already exists!')

    def delete_topic(self):
        logging.info(f'Deleting topic: {self.topic_path}')
        try:
            self.publisher.delete_topic(request={'topic': self.topic_path})
            return True
        except NotFound:
            logging.info(f'Topic {self.topic_path} NOT FOUND ...')
            return False

    def list_topics(self):
        project_path = f'projects/{self.env.project}'
        return self.publisher.list_topics(request={"project": project_path})

    def create_subscription(self, subscription_id):
        subscription_path = self.subscriber.subscription_path(self.env.project, subscription_id)
        with self.subscriber:
            subscription = self.subscriber.create_subscription(
                request={"name": subscription_path, "topic": self.topic_path}
            )

    def delete_subscription(self, subscription_id):
        subscription_path = self.subscriber.subscription_path(self.env.project, subscription_id)
        with self.subscriber:
            try:
                self.subscriber.delete_subscription(request={'subscription': subscription_path})
                return True
            except NotFound:
                logging.info(f'Subscription {subscription_id} NOT FOUND ...')
                return False

    def msg(self, **args):
        self.publisher.publish(self.topic_path, data=b'Cyber Arena PubSub Message', **args)
