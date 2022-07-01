import os
import sys
from datetime import datetime, timedelta
import yaml
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from google.cloud import pubsub_v1
from utilities_v2.globals import BuildConstants, Buckets
from utilities_v2.gcp.cloud_env import CloudEnv
from utilities_v2.gcp.bucket_manager import BucketManager
from utilities_v2.infrastructure_as_code.build_spec_to_cloud import BuildSpecToCloud
from v2.cloud_fn_utilities.fixed_arena_workout_build import FixedArenaWorkoutBuild
import time
from v2.cloud_fn_utilities.gcp.compute_manager import ComputeManager


__author__ = "Philip Huff, Bryce Ebsen"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff, Bryce Ebsen"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Production"

# Parse command line arguments
parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
parser.add_argument("-a", "--fixed-arena", default=None, help="Fixed Arena Specification to build")

args = vars(parser.parse_args())

# Set up parameters
fixed_arena_workout = args.get('fixed_arena_workout')


class TestFixedArenaWorkout:
    def __init__(self):
        self.env = CloudEnv()
        self.bm = BucketManager()

    def build(self):
        fixed_arena_yaml = self.bm.get(bucket=self.env.spec_bucket,
                                       file=f"{Buckets.Folders.FIXED_ARENA_WORKOUT}{fixed_arena_workout}.yaml")
        build_spec = yaml.safe_load(fixed_arena_yaml)
        build_spec['workspace_settings'] = {
            'count': 2,
            'registration_required': False,
            'student_list': [],
            'expires': (datetime.now() + timedelta(hours=3)).isoformat()
        }
        build_spec_to_cloud = BuildSpecToCloud(cyber_arena_spec=build_spec, debug=True)
        build_spec_to_cloud.commit()
        # fawb = FixedArenaWorkoutBuild(build_id=build_spec['id'], debug=True)
        fawb = FixedArenaWorkoutBuild(build_id='ikfxkfymhf', debug=True)
        # fawb.build()
        fawb.start()
        # fawb.stop()
        # fawb.delete()
        # fawb.nuke()


if __name__ == "__main__":
    #cln_server = ComputeManager(server_name='cln-stoc-web-server')
    #cln_server.build()

    fixed_arena_workout = 'stoc-workout' if not fixed_arena_workout else fixed_arena_workout
    TestFixedArenaWorkout().build()
