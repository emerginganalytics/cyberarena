from cloud_fn_utilities.globals import PubSub, DatastoreKeyTypes
from cloud_fn_utilities.gcp.pubsub_manager import PubSubManager
from cloud_fn_utilities.gcp.compute_manager import ComputeManager
from cloud_fn_utilities.gcp.datastore_manager import DataStoreManager
from cloud_fn_utilities.cyber_arena_objects.workout import Workout
from cloud_fn_utilities.cyber_arena_objects.fixed_arena_class import FixedArenaClass

__author__ = "Philip Huff"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff, Ryan Ebsen"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class QuarterHourlyMaintenance:
    def __init__(self, debug=False):
        self.debug = debug
        self.ds_workouts = DataStoreManager(key_type=DatastoreKeyTypes.WORKOUT)
        self.ds_fixed_arena_class = DataStoreManager(key_type=DatastoreKeyTypes.FIXED_ARENA_CLASS)
        self.pub_sub_mgr = PubSubManager(PubSub.Topics.CYBER_ARENA)

    def run(self):
        self._stop_lapsed()

    def _stop_lapsed(self):
        workouts_to_stop = self.ds_workouts.get_ready_for_shutoff()
        classes_to_stop = self.ds_fixed_arena_class.get_ready_for_shutoff()

        for workout_id in workouts_to_stop:
            if self.debug:
                Workout(build_id=workout_id).stop()
            else:
                self.pub_sub_mgr.msg(handler=PubSub.Handlers.CONTROL,
                                     cyber_arena_object=str(PubSub.CyberArenaObjects.WORKOUT.value),
                                     build_id=workout_id, action=str(PubSub.Actions.STOP.value))
        for class_id in classes_to_stop:
            if self.debug:
                FixedArenaClass(build_id=class_id).stop()
            else:
                self.pub_sub_mgr.msg(handler=PubSub.Handlers.CONTROL,
                                     cyber_arena_object=str(PubSub.CyberArenaObjects.FIXED_ARENA_CLASS.value),
                                     build_id=class_id, action=str(PubSub.Actions.STOP.value))
