import logging
from google.cloud import logging_v2

from cloud_fn_utilities.globals import PubSub
from cloud_fn_utilities.gcp.cloud_env import CloudEnv
from cloud_fn_utilities.gcp.compute_manager import ComputeManager
from cloud_fn_utilities.gcp.pubsub_manager import PubSubManager
from cloud_fn_utilities.cyber_arena_objects.fixed_arena_class import FixedArenaClass
from cloud_fn_utilities.cyber_arena_objects.fixed_arena import FixedArena
from cloud_fn_utilities.cyber_arena_objects.workout import Workout
from cloud_fn_utilities.cyber_arena_objects.unit import Unit

__author__ = "Philip Huff"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"

from cloud_fn_utilities.server_specific.display_proxy import DisplayProxy


class ControlHandler:
    def __init__(self, event_attributes, env_dict=None, debug=False):
        self.debug = debug
        self.env = CloudEnv(env_dict=env_dict) if env_dict else CloudEnv()
        self.env_dict = self.env.get_env()
        log_client = logging_v2.Client()
        log_client.setup_logging()
        self.event_attributes = event_attributes
        self.pub_sub_mgr = PubSubManager(PubSub.Topics.CYBER_ARENA.value, env_dict=self.env_dict)
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
        elif self.action == str(PubSub.Actions.STOP.value):
            self._stop()
        elif self.action == str(PubSub.Actions.DELETE.value):
            self._delete()
        elif self.action == str(PubSub.Actions.NUKE.value):
            self._nuke()
        elif self.action == str(PubSub.Actions.EXTEND_RUNTIME.value):
            self._extend_runtime()
        else:
            logging.error(f"Unsupported action supplied to the control handler")
            raise ValueError

    def _start(self):
        if self.cyber_arena_object == str(PubSub.CyberArenaObjects.SERVER.value):
            ComputeManager(server_name=self.build_id, env_dict=self.env_dict).start()
        elif self.cyber_arena_object == str(PubSub.CyberArenaObjects.FIXED_ARENA_CLASS.value):
            FixedArenaClass(build_id=self.build_id, debug=self.debug, env_dict=self.env_dict).start()
        elif self.cyber_arena_object == str(PubSub.CyberArenaObjects.FIXED_ARENA.value):
            pass
        elif self.cyber_arena_object == str(PubSub.CyberArenaObjects.WORKOUT.value):
            duration_hours = self.event_attributes.get('duration', 2)
            Workout(build_id=self.build_id, duration_hours=duration_hours, debug=self.debug, env_dict=self.env_dict).start()
        else:
            logging.error(f"Unsupported object passed to the control handler for action {self.action}")
            raise ValueError

    def _stop(self):
        if self.cyber_arena_object == str(PubSub.CyberArenaObjects.SERVER.value):
            ComputeManager(server_name=self.build_id, env_dict=self.env_dict).stop()
        elif self.cyber_arena_object == str(PubSub.CyberArenaObjects.FIXED_ARENA_CLASS.value):
            FixedArenaClass(build_id=self.build_id, debug=self.debug, env_dict=self.env_dict).stop()
        elif self.cyber_arena_object == str(PubSub.CyberArenaObjects.FIXED_ARENA.value):
            pass
        elif self.cyber_arena_object == str(PubSub.CyberArenaObjects.WORKOUT.value):
            Workout(build_id=self.build_id, debug=self.debug, env_dict=self.env_dict).stop()
        else:
            logging.error(f"Unsupported object passed to the control handler for action {self.action}")
            raise ValueError
            
    def _delete(self):
        if self.cyber_arena_object == str(PubSub.CyberArenaObjects.SERVER.value):
            ComputeManager(server_name=self.build_id, env_dict=self.env_dict).delete()
        elif self.cyber_arena_object == str(PubSub.CyberArenaObjects.FIXED_ARENA_CLASS.value):
            FixedArenaClass(build_id=self.build_id, debug=self.debug, env_dict=self.env_dict).delete()
        elif self.cyber_arena_object == str(PubSub.CyberArenaObjects.FIXED_ARENA.value):
            FixedArena(build_id=self.build_id, debug=self.debug, env_dict=self.env_dict).delete_fixed_arena()
        elif self.cyber_arena_object == str(PubSub.CyberArenaObjects.WORKOUT.value):
            Workout(build_id=self.build_id, debug=self.debug, env_dict=self.env_dict).delete()
        elif self.cyber_arena_object == str(PubSub.CyberArenaObjects.UNIT.value):
            Unit(build_id=self.build_id, debug=self.debug, env_dict=self.env_dict).delete()
        else:
            logging.error(f"Unsupported object {self.cyber_arena_object} passed to the control handler for "
                          f"action {self.action}")
            raise ValueError

    def _nuke(self):
        if self.cyber_arena_object == str(PubSub.CyberArenaObjects.SERVER.value):
            ComputeManager(server_name=self.build_id, env_dict=self.env_dict).nuke()
        elif self.cyber_arena_object == str(PubSub.CyberArenaObjects.FIXED_ARENA_CLASS.value):
            FixedArenaClass(build_id=self.build_id, debug=self.debug, env_dict=self.env_dict).nuke()
        elif self.cyber_arena_object == str(PubSub.CyberArenaObjects.FIXED_ARENA.value):
            pass
        elif self.cyber_arena_object == str(PubSub.CyberArenaObjects.WORKOUT.value):
            Workout(build_id=self.build_id, debug=self.debug, env_dict=self.env_dict).nuke()
        else:
            logging.error(f"Unsupported object passed to the control handler for action {self.action}")
            raise ValueError

    def _extend_runtime(self):
        duration = self.event_attributes.get('duration', 1)
        if self.cyber_arena_object == str(PubSub.CyberArenaObjects.WORKOUT.value):
            Workout(build_id=self.build_id, duration_hours=duration, debug=self.debug, env_dict=self.env_dict).extend_runtime()
        else:
            logging.error(f'Unsupported object passed to the control handler for action {self.action}')
            raise ValueError
