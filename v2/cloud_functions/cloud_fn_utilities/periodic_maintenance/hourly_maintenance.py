import time

from cloud_fn_utilities.gcp.pubsub_manager import PubSubManager
from cloud_fn_utilities.gcp.datastore_manager import DataStoreManager
from cloud_fn_utilities.gcp.cloud_env import CloudEnv
from cloud_fn_utilities.globals import PubSub, FixedArenaClassStates, DatastoreKeyTypes, UnitStates
from cloud_fn_utilities.state_managers.fixed_arena_states import FixedArenaStateManager
from cloud_fn_utilities.state_managers.workout_states import WorkoutStates
from cloud_fn_utilities.cyber_arena_objects.fixed_arena_class import FixedArenaClass
from cloud_fn_utilities.cyber_arena_objects.unit import Unit
from cloud_fn_utilities.state_managers.unit_states import UnitStateManager

__author__ = "Philip Huff"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class HourlyMaintenance:
    def __init__(self, debug=False, env_dict=None):
        self.debug = debug
        self.env = CloudEnv(env_dict=env_dict) if env_dict else CloudEnv()
        self.env_dict = self.env.get_env()
        self.pub_sub_mgr = PubSubManager(PubSub.Topics.CYBER_ARENA, env_dict=self.env_dict)
        self.fa_state_manager = FixedArenaStateManager()
        self.ds_units = DataStoreManager(key_type=DatastoreKeyTypes.UNIT)
        self.ds_classes = DataStoreManager(key_type=DatastoreKeyTypes.FIXED_ARENA_CLASS)

    def run(self):
        self._delete_expired_classes()
        self._delete_expired_units()

    def _delete_expired_classes(self):
        expired_classes = self.ds_classes.get_expired()
        for build_id in expired_classes:
            fac = DataStoreManager(key_type=DatastoreKeyTypes.FIXED_ARENA_CLASS, key_id=build_id).get()
            if not fac:
                continue
            fac_state = fac.get('state', None)
            if not fac_state:
                FixedArenaClass(build_id=build_id, env_dict=self.env_dict).mark_broken()
                continue

            if fac_state not in [FixedArenaClassStates.BROKEN.value, FixedArenaClassStates.DELETED.value]:
                if self.debug:
                    FixedArenaClass(build_id=build_id, debug=self.debug, env_dict=self.env_dict).delete()
                else:
                    self.pub_sub_mgr.msg(handler=PubSub.Handlers.CONTROL,
                                         cyber_arena_object=str(PubSub.CyberArenaObjects.FIXED_ARENA_CLASS.value),
                                         build_id=build_id, action=str(PubSub.Actions.DELETE.value))

    def _delete_expired_units(self):
        expired_units = self.ds_units.get_expired()
        for build_id in expired_units:
            unit_state_manager = UnitStateManager(build_id=build_id)
            if unit_state_manager.get_state() not in [UnitStates.DELETED.value]:
                if self.debug:
                    Unit(build_id=build_id, debug=self.debug, env_dict=self.env_dict).delete()
                else:
                    self.pub_sub_mgr.msg(handler=PubSub.Handlers.CONTROL,
                                         cyber_arena_object=str(PubSub.CyberArenaObjects.UNIT.value),
                                         build_id=build_id, action=str(PubSub.Actions.DELETE.value))
                    time.sleep(20)
