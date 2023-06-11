from google.cloud import datastore
from datetime import datetime, timedelta, timezone
import yaml
import random
import string
import requests
from main_app_utilities.global_objects.name_generator import NameGenerator
from main_app_utilities.globals import Buckets, PubSub, DatastoreKeyTypes
from main_app_utilities.gcp.cloud_env import CloudEnv
from main_app_utilities.gcp.bucket_manager import BucketManager
from cloud_fn_utilities.gcp.datastore_manager import DataStoreManager
from main_app_utilities.infrastructure_as_code.build_spec_to_cloud import BuildSpecToCloud
from main_app_utilities.lms.lms_canvas import LMSSpecCanvas

from cloud_fn_utilities.cyber_arena_objects.unit import Unit
from cloud_fn_utilities.cyber_arena_objects.workout import Workout


__author__ = "Philip Huff"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Production"


class TestUnit:
    def __init__(self, build_id=None, debug=True):
        self.env = CloudEnv()
        self.env_dict = self.env.get_env()
        self.bm = BucketManager()
        self.build_id = build_id if build_id else None
        self.debug = debug
        self.yaml = yaml.safe_load(open('test_unit.yaml'))

    def build(self, debug: bool = True):
        build_spec = DataStoreManager(key_type=DatastoreKeyTypes.CATALOG.value, key_id=self.yaml['unit_name']).get()
        if not build_spec:
            print(f"Invalid build spec name passed")
            return
        build_spec['instructor_id'] = self.yaml.get('instructor_id', 'philiphuff7@gmail.com')
        build_spec['test'] = True
        build_spec['workspace_settings'] = {
            'count': 1,
            'registration_required': False,
            'student_emails': [],
            'expires': (datetime.now(timezone.utc).replace(tzinfo=timezone.utc) + timedelta(days=10)).timestamp()
        }
        build_spec['join_code'] = ''.join(str(random.randint(0, 9)) for num in range(0, 6))

        if self.yaml.get('lms_integration', False):
            if self.yaml['lms_type'] == 'canvas':
                lms_spec_decorator = LMSSpecCanvas(build_spec=build_spec,
                                                   course_code=self.yaml['lms_course_code'],
                                                   due_at=self.yaml.get('lms_due_at', None),
                                                   time_limit=self.yaml.get('lms_time_limit', None),
                                                   allowed_attempts=self.yaml.get('lms_allowed_attempts', None),
                                                   lms_type=self.yaml['lms_type'])
            build_spec = lms_spec_decorator.decorate()

        build_spec_to_cloud = BuildSpecToCloud(cyber_arena_spec=build_spec, env_dict=self.env_dict)
        build_spec_to_cloud.commit(publish=False)
        self.build_id = build_spec_to_cloud.build_id

        if debug:
            print(f"Beginning to build a new unit with ID {self.build_id}")
            if build_spec.get('escape_room', None):
                team_names = NameGenerator(count=build_spec['workspace_settings']['count']).generate()
                for i in range(build_spec['workspace_settings']['count']):
                    if build_spec.get('escape_room', None):
                        claimed_by = {'team_name': team_names[i]}
                    else:
                        claimed_by = {'student_email': f'example{i}@ualr.edu'}
                    workout_id = ''.join(random.choice(string.ascii_lowercase) for j in range(10))
                    print(f'\t...building workout with ID {workout_id}')
                    unit = Unit(build_id=self.build_id, child_id=workout_id, form_data=claimed_by, debug=debug, force=True,
                                env_dict=self.env_dict)
                    unit.build()
            else:
                unit = Unit(build_id=self.build_id, debug=True, env_dict=self.env_dict)
                unit.build()
                self._build_one_workout()


            print(f"Finished building")

    def start(self):
        Unit(build_id=self.build_id, debug=self.debug).start()

    def stop(self):
        Unit(build_id=self.build_id, debug=True).stop()

    def delete(self):
        Unit(build_id=self.build_id, debug=self.debug).delete()

    def question_completion(self):
        ds_unit = DataStoreManager(key_type=DatastoreKeyTypes.UNIT, key_id=self.build_id)
        unit = ds_unit.get()
        workouts = ds_unit.get_children(child_key_type=DatastoreKeyTypes.WORKOUT, parent_id=self.build_id)
        for workout in workouts:
            workout_id = workout['id']
            for question in unit['lms_quiz']['questions']:
                if question_key := question.get('question_key', None):
                    data = {
                        "question_key": question_key,
                    }
                    response = requests.put(f"http://localhost:8080//api/unit/workout/{workout_id}", json=data)

    def _build_one_workout(self):
        build_one = str(input(f"Would you like to test the workout build at this time? (y/N)"))
        if build_one and build_one.upper()[0] == "Y":
            ds_unit = DataStoreManager(key_type=DatastoreKeyTypes.UNIT, key_id=self.build_id)
            workouts = ds_unit.get_children(child_key_type=DatastoreKeyTypes.WORKOUT, parent_id=self.build_id)
            workout_id = workouts[0]['id']
            print(f"Beginning to build workout {workout_id}...")
            workout = Workout(build_id=workout_id, debug=True)
            print(f"Finished building workout {workout_id}")
            workout.build()


if __name__ == "__main__":
    print(f"Unit v2 Tester.")
    delete_first = str(input(f"Do you want to delete a test unit first? (y/N)"))
    if delete_first and delete_first.upper()[0] == "Y":
        delete_unit = str(input(f"What is the unit ID that you want to delete?"))
        TestUnit(build_id=delete_unit, debug=False).delete()
        print(f"Unit deletion was successful!")
    build_first = str(input(f"Build the test unit described in test_unit.yaml? (Y/n)"))
    if not build_first or build_first.upper()[0] == "Y":
        test_unit = TestUnit()
        test_unit.build()
    else:
        test_unit_id = str(input(f"Which unit ID do you want to test?"))
        test_unit = TestUnit(build_id=test_unit_id, debug=False)
    while True:
        action = str(input(f"What action are you wanting to test [QUIT], {PubSub.Actions.START.name}, "
                           f"{PubSub.Actions.STOP.name}, {PubSub.Actions.DELETE.name}, or ASSESS?"))
        if not action or action.upper()[0] == "Q":
            break
        if action == PubSub.Actions.START.name:
            test_unit.start()
        elif action == PubSub.Actions.STOP.name:
            test_unit.stop()
        elif action == PubSub.Actions.DELETE.name:
            test_unit.delete()
            break
        elif action.upper()[0] == "A":
            test_unit.question_completion()
