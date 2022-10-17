import datetime
import logging
from google.cloud import logging_v2
from cloud_fn_utilities.globals import PubSub, DatastoreKeyTypes
from cloud_fn_utilities.gcp.cloud_env import CloudEnv
from cloud_fn_utilities.gcp.datastore_manager import DataStoreManager
from cloud_fn_utilities.gcp.compute_manager import ComputeManager

__author__ = "Andrew Bomberger"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Andrew Bomberger, Zachary Long"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class BotnetHandler:
    def __init__(self, event_attributes):
        """
        event_attributes expects the following objects:
            - build_id: attack template id
            - network: fixed-arena to inject into
            - mode: Attack or inject
            - args: Template arguments
            - expires: Time event expires on (possibly not needed)
        :param event_attributes:
        """
        self.env = CloudEnv()
        log_client = logging_v2.Client()
        log_client.setup_logging()
        self.event_attributes = event_attributes
        self.kind = DatastoreKeyTypes.CYBERARENA_ATTACK.value
        self.attack_obj = {}

    def route(self):
        if 'build' in self.event_attributes:
            self.build_agent()

    def build_agent(self):
        pass

    def __create_ds_entry(self, attack_obj):
        """ Takes input data and creates a datastore entry related to the attack
            TODO: Might need to move this to attack_build_to_cloud class
        """
        attack_ds = DataStoreManager().ds_client
        attack_ds.get(self.kind)
        self.attack_obj = {
            'id': '',  # ID of attack
            'parent_id': attack_obj['parent_id'],  # ID of attack template
            'mode': attack_obj['mode'],  # Either attack or inject
            'state': 'TBD',  # TODO: Create botnet states enum
            'time': datetime.datetime.now(),  # Time build was initiated
            'network': attack_obj['network'],  # ID of fixed-arena to inject attack into
            'args': attack_obj['args'],  # args used to build the script
        }

    def __build_attack(self):
        """
        TODO: build attack based on input attack_id
        """
        pass

    def __build_args_command(self, args):
        """
        Takes script args and constructs the command based on those args and attack type
        """
        pass
