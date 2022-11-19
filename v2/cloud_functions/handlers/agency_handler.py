import logging
from google.cloud import logging_v2
from cloud_fn_utilities.globals import PubSub, DatastoreKeyTypes
from cloud_fn_utilities.gcp.cloud_env import CloudEnv
from cloud_fn_utilities.gcp.datastore_manager import DataStoreManager
from cloud_fn_utilities.gcp.pubsub_manager import PubSubManager
from cloud_fn_utilities.cyber_arena_objects.cyberarena_agent import CyberArenaAgent

__author__ = "Andrew Bomberger"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Andrew Bomberger"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class AgencyHandler:
    def __init__(self, event_attributes, debug=False):
        self.event_attributes = event_attributes
        self.debug = debug
        log_client = logging_v2.Client()
        log_client.setup_logging()

    def route(self):
        action = self.event_attributes.get('action', None)
        if not action:
            logging.error(f'No action provided in cloud function agency handler')
            raise ValueError
        if action == str(PubSub.BuildActions.CYBER_ARENA_ATTACK.value):
            attack_id = self.event_attributes.get('attack_id', None)
            if 'attack_id' not in self.event_attributes:
                logging.error(f"No build_id for agency handler with action {action}")
                raise ValueError
            CyberArenaAgent(build_id=self.event_attributes['build_id']).send_command(self.event_attributes)
        elif action == str(PubSub.BuildActions.CYBER_ARENA_WEAKNESS.value):
            pass

# [ eof ]
