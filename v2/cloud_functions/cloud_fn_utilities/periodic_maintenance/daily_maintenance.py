from cloud_fn_utilities.gcp.cloud_env import CloudEnv
from cloud_fn_utilities.gcp.datastore_manager import DataStoreManager
from cloud_fn_utilities.gcp.pubsub_manager import PubSubManager
from cloud_fn_utilities.globals import PubSub, DatastoreKeyTypes, get_current_timestamp_utc
from cloud_fn_utilities.gcp.compute_manager import ProjectComputeManager
from cloud_fn_utilities.database.vulnerabilities import Vulnerabilities
from cloud_fn_utilities.cyber_arena_objects.vulnerabilities import Vulnerabilities
from cloud_fn_utilities.cyber_arena_objects.fixed_arena_class import FixedArenaClass
from cloud_fn_utilities.send_mail.send_mail import SendMail
from cloud_fn_utilities.cyber_arena_objects.workout import Workout

__author__ = "Philip Huff"
__copyright__ = "Copyright 2023, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff, Ryan Ebsen, Bryce Ebsen"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Production"


class DailyMaintenance:
    def __init__(self, debug=False, env_dict=None):
        self.env = CloudEnv(env_dict=env_dict) if env_dict else CloudEnv()
        self.env_dict = self.env.get_env()
        self.compute_manager = ProjectComputeManager(env_dict=self.env.get_env())
        self.pub_sub_mgr = PubSubManager(PubSub.Topics.CYBER_ARENA, env_dict=self.env.get_env())
        self.debug = debug
        self.ds = DataStoreManager(key_type=DatastoreKeyTypes.UNIT)

    def run(self):
        self._stop_all()
        self._notify_expiring_units()
        Vulnerabilities().update()

    def _stop_all(self):
        running_workouts = DataStoreManager(key_type=DatastoreKeyTypes.WORKOUT).get_running()
        for workout in running_workouts:
            workout_id = workout['id']
            if self.debug:
                Workout(build_id=workout_id, env_dict=self.env.get_env()).stop()
            else:
                self.pub_sub_mgr.msg(handler=str(PubSub.Handlers.CONTROL.value), action=str(PubSub.Actions.STOP.value),
                                     build_id=str(workout_id),
                                     cyber_arena_object=str(PubSub.CyberArenaObjects.WORKOUT.value))
        classes_to_stop = DataStoreManager(key_type=DatastoreKeyTypes.FIXED_ARENA_CLASS).get_running()
        for fa_class in classes_to_stop:
            class_id = fa_class['id']
            if self.debug:
                FixedArenaClass(build_id=class_id, env_dict=self.env_dict).stop()
            else:
                self.pub_sub_mgr.msg(handler=PubSub.Handlers.CONTROL,
                                     cyber_arena_object=str(PubSub.CyberArenaObjects.FIXED_ARENA_CLASS.value),
                                     build_id=class_id, action=str(PubSub.Actions.STOP.value))
        self.compute_manager.stop_everything()

    def _notify_expiring_units(self):
        """
        sends an email to the owner of all units that expire within 48 hours
        @return:
        """
        expiring_units = self.ds.get_expiring_units()
        for unit_id in expiring_units:
            unit = self.ds.get(key_type=DatastoreKeyTypes.UNIT, key_id=unit_id)
            workout_name = unit['summary']['name']
            instructor = unit['instructor_id']
            num_workouts = unit['workspace_settings']['count']
            expires = unit['workspace_settings']['expires']
            hours_until_expired = round((expires - get_current_timestamp_utc()) / 3600)
            if hours_until_expired >= 0:
                SendMail().send_expiring_units(unit_id=unit_id, workout_name=workout_name, instructor=instructor,
                                               num_workouts=num_workouts, hours_until_expires=hours_until_expired)
