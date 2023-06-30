from google.cloud import datastore
from datetime import datetime, timedelta, timezone
import yaml
from main_app_utilities.globals import Buckets, PubSub
from main_app_utilities.gcp.cloud_env import CloudEnv
from main_app_utilities.gcp.bucket_manager import BucketManager
from main_app_utilities.infrastructure_as_code.build_spec_to_cloud import BuildSpecToCloud
from cloud_fn_utilities.cyber_arena_objects.workout import Workout


__author__ = "Philip Huff"
__copyright__ = "Copyright 2023, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Production"


class TestWorkout:
    def __init__(self, build_id=None, debug=True):
        self.env = CloudEnv()
        self.bm = BucketManager()
        self.build_id = build_id if build_id else None
        self.debug = debug

    def build(self):
        Workout(build_id=self.build_id, debug=self.debug).build()

    def start(self):
        Workout(build_id=self.build_id, debug=self.debug).start()

    def stop(self):
        Workout(build_id=self.build_id, debug=True).stop()

    def delete(self):
        Workout(build_id=self.build_id, debug=self.debug).delete()


if __name__ == "__main__":
    print(f"Workout v2 Tester.")

    test_workout_id = str(input(f"Which workout do you want to test? "))
    debug_response = str(input(f"Do you want to debug? Y/n "))
    debug = False if debug_response.upper() == "N" else True
    test_workout = TestWorkout(build_id=test_workout_id, debug=debug)
    while True:
        action = str(input(f"What action are you wanting to test [QUIT],{PubSub.Actions.BUILD.name}, "
                           f"{PubSub.Actions.START.name}, {PubSub.Actions.STOP.name}, or "
                           f"{PubSub.Actions.DELETE.name}?"))
        if not action or action.upper()[0] == "Q":
            break

        if action == PubSub.Actions.START.name:
            test_workout.start()
        elif action == PubSub.Actions.STOP.name:
            test_workout.stop()
        elif action == PubSub.Actions.DELETE.name:
            test_workout.delete()
        elif action == PubSub.Actions.BUILD.name:
            test_workout.build()
