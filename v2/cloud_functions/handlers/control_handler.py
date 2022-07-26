import logging
from google.cloud import logging_v2

from cloud_fn_utilities.globals import PubSub
from cloud_fn_utilities.gcp.cloud_env import CloudEnv
from cloud_fn_utilities.gcp.compute_manager import ComputeManager
from cloud_fn_utilities.gcp.pubsub_manager import PubSubManager
from cloud_fn_utilities.cyber_arena_objects.fixed_arena_class import FixedArenaClass

__author__ = "Philip Huff"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class ControlHandler:
    def __init__(self, event_attributes, debug=False):
        self.debug = debug
        self.env = CloudEnv()
        log_client = logging_v2.Client()
        log_client.setup_logging()
        self.event_attributes = event_attributes
        self.pub_sub_mgr = PubSubManager(PubSub.Topics.CYBER_ARENA)
        self.action = self.event_attributes.get('action', None)
        self.cyber_arena_object = self.event_attributes.get('cyber_arena_object', None)
        self.build_id = self.event_attributes.get('build_id', None)
        if not self.action:
            logging.error(f"No action provided in cloud function control handler")
            raise ValueError
        if not self.cyber_arena_object:
            logging.error(f"No cyber arena object provided for control handler with action {self.action}")
            raise ValueError
        if not self.build_id:
            logging.error(f"No build id provided for control handler with action {self.action}")
            raise ValueError

    def route(self):
        if self.action == str(PubSub.Actions.START.value):
            self._start()
        elif self.action == str(PubSub.Actions.DELETE.value):
            self._delete()
        else:
            logging.error(f"Unsupported action supplied to the control handler")
            raise ValueError

    def _start(self):
        # TODO: Fill out the start functions here.
        if self.cyber_arena_object == str(PubSub.CyberArenaObjects.SERVER.value):
            ComputeManager(server_name=self.build_id).start()

    def _stop(self):
        if self.cyber_arena_object == str(PubSub.CyberArenaObjects.SERVER.value):
            ComputeManager(server_name=self.build_id).stop()
            
    def _delete(self):
        if self.cyber_arena_object == str(PubSub.CyberArenaObjects.SERVER.value):
            ComputeManager(server_name=self.build_id).delete()
        elif self.cyber_arena_object == str(PubSub.CyberArenaObjects.FIXED_ARENA_CLASS.value):
            FixedArenaClass(build_id=self.build_id, debug=self.debug).delete()
        elif self.cyber_arena_object == str(PubSub.CyberArenaObjects.FIXED_ARENA.value):
            pass
        else:
            logging.error(f"Unsupported object passed to the control handler for action {self.action}")
            raise ValueError
