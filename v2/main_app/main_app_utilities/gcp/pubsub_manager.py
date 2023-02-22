from google.cloud import logging_v2
from google.cloud import pubsub_v1

from main_app_utilities.gcp.cloud_env import CloudEnv

__author__ = "Philip Huff"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class PubSubManager:
    def __init__(self, topic, env_dict=None):
        self.env = CloudEnv(env_dict=env_dict) if env_dict else CloudEnv()
        log_client = logging_v2.Client()
        log_client.setup_logging()
        self.publisher = pubsub_v1.PublisherClient()
        self.topic_path = self.publisher.topic_path(self.env.project, topic)

    def msg(self, **args):
        self.publisher.publish(self.topic_path, data=b'Cyber Arena PubSub Message', **args)
