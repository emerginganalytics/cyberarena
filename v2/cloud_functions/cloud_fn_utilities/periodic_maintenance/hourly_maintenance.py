import time

from cloud_fn_utilities.gcp.pubsub_manager import PubSubManager
from cloud_fn_utilities.gcp.datastore_manager import DataStoreManager
from cloud_fn_utilities.gcp.cloud_env import CloudEnv
from cloud_fn_utilities.gcp.cloud_logger import Logger
from cloud_fn_utilities.globals import PubSub, FixedArenaClassStates, DatastoreKeyTypes, UnitStates
from cloud_fn_utilities.state_managers.fixed_arena_states import FixedArenaStateManager
from cloud_fn_utilities.state_managers.workout_states import WorkoutStates
from cloud_fn_utilities.cyber_arena_objects.fixed_arena_class import FixedArenaClass
from cloud_fn_utilities.cyber_arena_objects.unit import Unit
from cloud_fn_utilities.cyber_arena_objects.workout import Workout
from cloud_fn_utilities.state_managers.unit_states import UnitStateManager
from cloud_fn_utilities.state_managers.workout_states import WorkoutStateManager
from cloud_fn_utilities.lms.canvas.lms_canavas_synchronizer import LMSCanvasSynchronizer
from cloud_fn_utilities.gcp.iot_manager import IotManager

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
        self.logger = Logger("cloud_functions.hourly_maintenance").logger
        self.debug = debug
        self.env = CloudEnv(env_dict=env_dict) if env_dict else CloudEnv()
        self.env_dict = self.env.get_env()
        self.pub_sub_mgr = PubSubManager(PubSub.Topics.CYBER_ARENA.value, env_dict=self.env_dict)
        self.fa_state_manager = FixedArenaStateManager()
        self.ds_units = DataStoreManager(key_type=DatastoreKeyTypes.UNIT)
        self.ds_classes = DataStoreManager(key_type=DatastoreKeyTypes.FIXED_ARENA_CLASS)
        self.ds_workouts = DataStoreManager(key_type=DatastoreKeyTypes.WORKOUT)

    def run(self):
        self.logger.info(f"hourly maintenance: beginning to delete expired classes")
        self._delete_expired_classes()
        self.logger.info(f"hourly maintenance: completed deleting expired classes")
        self.logger.info(f"hourly maintenance: beginning to delete expired units")
        self._delete_expired_units()
        self.logger.info(f"hourly maintenance: completed deleting expired units")
        self.logger.info(f"hourly maintenance: beginning to delete expired workouts")
        self._delete_expired_workouts()
        self.logger.info(f"hourly maintenance: completed deleting expired workouts")
        self.logger.info(f"hourly maintenance: beginning to sync LMS students with active workouts")
        self._lms_sync()
        self.logger.info(f"hourly maintenance: completed sync'ing LMS students")

    def _delete_expired_classes(self):
        expired_classes = self.ds_classes.get_expired()
        self.logger.info(f"\t...deleting {len(expired_classes)} expired classes")
        for build_id in expired_classes:
            fac = DataStoreManager(key_type=DatastoreKeyTypes.FIXED_ARENA_CLASS, key_id=build_id).get()
            if not fac:
                continue
            fac_state = fac.get('state', None)
            if not fac_state:
                FixedArenaClass(build_id=build_id, env_dict=self.env_dict).mark_broken()
                continue

            if fac_state not in [FixedArenaClassStates.DELETED.value]: #FixedArenaClassStates.BROKEN.value,
                if self.debug:
                    FixedArenaClass(build_id=build_id, debug=self.debug, env_dict=self.env_dict).delete()
                else:
                    self.pub_sub_mgr.msg(handler=PubSub.Handlers.CONTROL,
                                         cyber_arena_object=str(PubSub.CyberArenaObjects.FIXED_ARENA_CLASS.value),
                                         build_id=build_id, action=str(PubSub.Actions.DELETE.value))

    def _delete_expired_units(self):
        expired_units = self.ds_units.get_expired()
        self.logger.info(f"\t...deleting {len(expired_units)} expired units")
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

    def _delete_expired_workouts(self):
        """
        For long running units used in asynchronous classes, workouts may be deleted before the unit expires. This
        keeps the project clear of stale workouts during the asynchronous class.
        """
        expired_workouts = self.ds_workouts.get_expired()
        self.logger.info(f"\t...deleting {len(expired_workouts)} expired workouts")
        for build_id in expired_workouts:
            workout_state_manager = WorkoutStateManager(initial_build_id=build_id)
            if workout_state_manager.get_state() not in [WorkoutStates.DELETED.value]:
                if self.debug:
                    Workout(build_id=build_id, debug=self.debug, env_dict=self.env_dict).delete()
                else:
                    self.pub_sub_mgr.msg(handler=PubSub.Handlers.CONTROL,
                                         cyber_arena_object=str(PubSub.CyberArenaObjects.WORKOUT.value),
                                         build_id=build_id, action=str(PubSub.Actions.DELETE.value))
                    time.sleep(20)

    def _lms_sync(self):
        """
        LMS units may have students added throughout the course, and this adds their workouts to units when a new
        student gets added to the LMS
        """
        LMSCanvasSynchronizer().sync_units_with_class_list()
