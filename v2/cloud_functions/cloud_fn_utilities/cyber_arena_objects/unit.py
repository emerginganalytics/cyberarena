import json
import random
import string
from datetime import datetime, timezone
from netaddr import IPNetwork, IPAddress, iter_iprange

from cloud_fn_utilities.gcp.cloud_env import CloudEnv
from cloud_fn_utilities.gcp.vpc_manager import VpcManager
from cloud_fn_utilities.gcp.datastore_manager import DataStoreManager
from cloud_fn_utilities.gcp.firewall_rule_manager import FirewallManager
from cloud_fn_utilities.gcp.pubsub_manager import PubSubManager
from cloud_fn_utilities.gcp.compute_manager import ComputeManager
from cloud_fn_utilities.gcp.cloud_logger import Logger
from cloud_fn_utilities.globals import DatastoreKeyTypes, PubSub, BuildConstants, UnitStates, WorkoutStates
from cloud_fn_utilities.cyber_arena_objects.workout import Workout
from cloud_fn_utilities.state_managers.unit_states import UnitStateManager

__author__ = "Philip Huff"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class Unit:
    def __init__(self, build_id, child_id=None, form_data=None, debug=False, force=False, env_dict=None):
        self.unit_id = build_id
        self.workout_id = child_id
        self.form_data = form_data
        self.debug = debug
        self.force = force
        self.env = CloudEnv(env_dict=env_dict) if env_dict else CloudEnv()
        self.env_dict = self.env.get_env()
        self.logger = Logger("cloud_functions.unit").logger
        self.s = UnitStates
        self.pubsub_manager = PubSubManager(PubSub.Topics.CYBER_ARENA.value, env_dict=self.env_dict)
        self.ds = DataStoreManager(key_type=DatastoreKeyTypes.UNIT, key_id=self.unit_id)
        self.unit = self.ds.get()
        if not self.unit:
            self.logger.error(f"The datastore record for {self.unit_id} no longer exists!")
            raise LookupError
        self.workout_ids = []

    def build(self):
        self._create_and_build_workouts()

    def start(self):
        workouts = self.ds.get_children(child_key_type=DatastoreKeyTypes.WORKOUT, parent_id=self.unit_id)
        for workout in workouts:
            if self.debug:
                workout = Workout(build_id=id, debug=self.debug, env_dict=self.env_dict)
                workout.delete()
            else:
                self.pubsub_manager.msg(handler=str(PubSub.Handlers.CONTROL.value),
                                        action=str(PubSub.Actions.START.value),
                                        cyber_arena_object=str(PubSub.CyberArenaObjects.WORKOUT.value),
                                        build_id=str(workout.key.name))

    def stop(self):
        workouts = self.ds.get_children(child_key_type=DatastoreKeyTypes.WORKOUT, parent_id=self.unit_id)
        for workout in workouts:
            Workout(build_id=workout.key.name, debug=self.debug, env_dict=self.env_dict).stop()

    def delete(self):
        workouts = self.ds.get_children(child_key_type=DatastoreKeyTypes.WORKOUT, parent_id=self.unit_id)
        for workout in workouts:
            if self.debug:
                Workout(build_id=workout.key.name, debug=self.debug, env_dict=self.env_dict).delete()
            else:
                self.pubsub_manager.msg(handler=str(PubSub.Handlers.CONTROL.value),
                                        action=str(PubSub.Actions.DELETE.value),
                                        cyber_arena_object=str(PubSub.CyberArenaObjects.WORKOUT.value),
                                        build_id=str(workout.key.name))
        unit_state_manager = UnitStateManager(build_id=self.unit_id)
        if unit_state_manager.are_workouts_deleted():
            unit_state_manager.state_transition(new_state=UnitStates.DELETED)
        else:
            self.logger.error(f"Unit {self.unit_id} is not deleted!")

    def nuke(self):
        workouts = self.ds.get_children(child_key_type=DatastoreKeyTypes.WORKOUT, parent_id=self.unit_id)
        for workout in workouts:
            Workout(build_id=workout.key.name, debug=self.debug, env_dict=self.env_dict).nuke()

    def mark_broken(self):
        self.unit['state'] = self.s.BROKEN
        self.ds.put(self.unit)

    def get_build_id(self):
        return self.unit_id

    def _create_and_build_workouts(self):
        workout_datastore = DataStoreManager()
        count = min(self.env.max_workspaces, self.unit['workspace_settings']['count'])
        workout_query = DataStoreManager(key_type=DatastoreKeyTypes.WORKOUT).query()
        workout_list = [i for i in workout_query if i['parent_id'] == self.unit_id]
        if workout_list:
            if len(workout_list) >= count:
                self.logger.error(f"Requested build for unit {self.unit_id} failed; Unit is at max capacity")
                raise ValueError
        student_email = self.form_data.get('student_email', None)
        team_name = self.form_data.get('team_name', None)
        if student_email and self.workout_id:
            workout_record = self._create_workout_record()
            workout_record['student_email'] = student_email
            student_name = self.form_data.get('student_name', None)
            if student_name:
                workout_record['student_name'] = student_name
        elif team_name and self.workout_id:
            workout_record = self._create_workout_record()
            workout_record['team_name'] = team_name
        else:
            self.logger.error(f'Invalid or missing claimed_by values given for unit {self.unit_id}')
            raise ValueError
        workout_datastore.put(workout_record, key_type=DatastoreKeyTypes.WORKOUT, key_id=self.workout_id)
        if self.debug:
            workout = Workout(build_id=self.workout_id, debug=self.debug, env_dict=self.env_dict)
            workout.build()
        else:
            self.pubsub_manager.msg(handler=str(PubSub.Handlers.BUILD.value),
                                    action=str(PubSub.BuildActions.WORKOUT.value),
                                    key_type=str(DatastoreKeyTypes.WORKOUT.value),
                                    build_id=str(self.workout_id))

    def _create_workout_record(self):
        workout_record = {
            'id': self.workout_id,
            'parent_id': self.unit_id,
            'parent_build_type': BuildConstants.BuildType.UNIT,
            'build_type': BuildConstants.BuildType.WORKOUT,
            'creation_timestamp': datetime.now(timezone.utc).replace(tzinfo=timezone.utc).timestamp(),
            'state': WorkoutStates.START.value,
        }
        if self.unit.get('networks'):
            workout_record['networks'] = self.unit['networks']
            workout_record['servers'] = self.unit['servers']
            workout_record['firewall_rules'] = self.unit.get('firewall_rules', None)
        if self.unit.get('web_applications'):
            processed_web_applications = []
            for web_application in self.unit['web_applications']:
                processed_web_application = {
                    'name': web_application['name'],
                    'url': f"https://{web_application['host_name']}{self.env.dns_suffix}"
                           f"{web_application['starting_directory']}/{self.workout_id}",
                    'starting_directory': web_application['starting_directory'],
                }
                processed_web_applications.append(processed_web_application)
            workout_record['web_applications'] = processed_web_applications
        escape_room_spec = self.unit.get('escape_room', None)
        if escape_room_spec:
            workout_record['escape_room'] = escape_room_spec
        else:
            if self.unit.get('assessment', None):
                workout_record['assessment'] = self.unit['assessment']
        if self.debug:
            workout_record['test'] = True
        return workout_record
