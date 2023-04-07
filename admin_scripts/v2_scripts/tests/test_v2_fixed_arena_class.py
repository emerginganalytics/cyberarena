from google.cloud import datastore
from datetime import datetime, timedelta, timezone
import yaml
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from main_app_utilities.globals import Buckets, PubSub, DatastoreKeyTypes
from main_app_utilities.gcp.cloud_env import CloudEnv
from main_app_utilities.gcp.datastore_manager import DataStoreManager
from main_app_utilities.gcp.bucket_manager import BucketManager
from main_app_utilities.infrastructure_as_code.build_spec_to_cloud import BuildSpecToCloud
from cloud_fn_utilities.cyber_arena_objects.fixed_arena_class import FixedArenaClass


__author__ = "Philip Huff"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Production"


# Parse command line arguments
parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
parser.add_argument("-a", "--fixed-arena-class", default=None, help="Fixed Arena Specification to build")
parser.add_argument("-b", "--build_id", default=None, help="Build ID")
parser.add_argument("-x", "--action", default=None, help="Action to take")

args = vars(parser.parse_args())

# Set up parameters
fixed_arena_class = args.get('fixed-arena-class', None)
build_id = args.get('build_id', None)
action = args.get('action', None)


class TestFixedArenaWorkout:
    def __init__(self, debug=True):
        self.env = CloudEnv()
        self.debug = debug

    def build(self):
        build_spec = DataStoreManager(key_type=DatastoreKeyTypes.CATALOG, key_id='linux-stoc-class').get()
        build_spec['workspace_settings'] = {
            'count': 2,
            'registration_required': False,
            'student_emails': [],
            'expires': (datetime.now(timezone.utc).replace(tzinfo=timezone.utc) + timedelta(hours=3)).timestamp()
        }
        build_spec['add_attacker'] = False
        build_spec_to_cloud = BuildSpecToCloud(cyber_arena_spec=build_spec, debug=self.debug)
        build_spec_to_cloud.commit()
        fac = FixedArenaClass(build_id=build_spec['id'], debug=self.debug, force=True)
        fac.build()

    def start(self):
        FixedArenaClass(build_id=build_id, debug=self.debug).start()

    def stop(self):
        FixedArenaClass(build_id=build_id, debug=self.debug).stop()

    def delete(self):
        FixedArenaClass(build_id=build_id, debug=self.debug).delete()


if __name__ == "__main__":
    fixed_arena_class = 'stoc-class' if not fixed_arena_class else fixed_arena_class
    if not action or action == PubSub.Actions.BUILD.name:
        TestFixedArenaWorkout().build()
    elif action == PubSub.Actions.START.name:
        TestFixedArenaWorkout().start()
    elif action == PubSub.Actions.STOP.name:
        TestFixedArenaWorkout().stop()
    elif action == PubSub.Actions.DELETE.name:
        TestFixedArenaWorkout().delete()
