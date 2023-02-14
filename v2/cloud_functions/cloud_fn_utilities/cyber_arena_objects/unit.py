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

__author__ = "Philip Huff"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class Unit:
    def __init__(self, build_id, debug=False, force=False):
        self.unit_id = build_id
        self.debug = debug
        self.force = force
        self.env = CloudEnv()
        self.logger = Logger("cloud_functions.unit").logger
        self.s = UnitStates
        self.pubsub_manager = PubSubManager(PubSub.Topics.CYBER_ARENA)
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
            Workout(build_id=workout.key.name, debug=self.debug).start()

    def stop(self):
        workouts = self.ds.get_children(child_key_type=DatastoreKeyTypes.WORKOUT, parent_id=self.unit_id)
        for workout in workouts:
            Workout(build_id=workout.key.name, debug=self.debug).stop()

    def delete(self):
        workouts = self.ds.get_children(child_key_type=DatastoreKeyTypes.WORKOUT, parent_id=self.unit_id)
        for workout in workouts:
            Workout(build_id=workout.key.name, debug=self.debug).delete()

    def nuke(self):
        workouts = self.ds.get_children(child_key_type=DatastoreKeyTypes.WORKOUT, parent_id=self.unit_id)
        for workout in workouts:
            Workout(build_id=workout.key.name, debug=self.debug).nuke()

    def mark_broken(self):
        self.unit['state'] = self.s.BROKEN
        self.ds.put(self.unit)

    def get_build_id(self):
        return self.unit_id

    def _create_and_build_workouts(self):
        workout_datastore = DataStoreManager()
        registration_required = self.unit['workspace_settings'].get('registration_required', False)
        if registration_required:
            student_emails = self.unit['workspace_settings']['student_emails']
            student_names = self.unit['workspace_settings']['student_names']
            count = min(self.env.max_workspaces, len(student_names))
        else:
            count = min(self.env.max_workspaces, self.unit['workspace_settings']['count'])

        for i in range(count):
            id = ''.join(random.choice(string.ascii_lowercase) for j in range(10))
            workout_record = {
                'id': id,
                'parent_id': self.unit_id,
                'parent_build_type': BuildConstants.BuildType.UNIT,
                'build_type': BuildConstants.BuildType.WORKOUT,
                'creation_timestamp': datetime.now(timezone.utc).replace(tzinfo=timezone.utc).timestamp(),
                'registration_required': registration_required,
                'state': WorkoutStates.START.value
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
                               f"{web_application['starting_directory']}/{id}"
                    }
                    processed_web_applications.append(processed_web_application)
                workout_record['web_applications'] = processed_web_applications
            escape_room_spec = self.unit.get('escape_room', None)
            if escape_room_spec:
                workout_record['escape_room'] = escape_room_spec
            else:
                if self.unit.get('assessment', None):
                    workout_record['assessment'] = self.unit['assessment']
            if registration_required:
                workout_record['student_email'] = student_emails[i]
                workout_record['student_name'] = student_names[i]
            if self.debug:
                workout_record['test'] = True
            workout_datastore.put(workout_record, key_type=DatastoreKeyTypes.WORKOUT, key_id=id)
            if self.debug:
                workout = Workout(build_id=id, debug=self.debug)
                workout.build()
            else:
                self.pubsub_manager.msg(handler=str(PubSub.Handlers.BUILD.value),
                                        action=str(PubSub.BuildActions.WORKOUT.value),
                                        key_type=str(DatastoreKeyTypes.WORKOUT.value),
                                        build_id=str(id))
