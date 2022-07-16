from google.cloud import datastore
from datetime import datetime, timedelta, timezone
import yaml
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from utilities.globals import Buckets
from utilities.gcp.cloud_env import CloudEnv
from utilities.gcp.bucket_manager import BucketManager
from utilities.infrastructure_as_code.build_spec_to_cloud import BuildSpecToCloud
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
parser.add_argument("-a", "--fixed-arena", default=None, help="Fixed Arena Specification to build")

args = vars(parser.parse_args())

# Set up parameters
fixed_arena_class = args.get('fixed_arena_class')


class TestFixedArenaWorkout:
    def __init__(self):
        self.env = CloudEnv()
        self.bm = BucketManager()

    def build(self):
        fixed_arena_yaml = self.bm.get(bucket=self.env.spec_bucket,
                                       file=f"{Buckets.Folders.SPECS}{fixed_arena_class}.yaml")
        build_spec = yaml.safe_load(fixed_arena_yaml)
        build_spec['workspace_settings'] = {
            'count': 2,
            'registration_required': False,
            'student_list': [],
            'expires': (datetime.now(timezone.utc).replace(tzinfo=timezone.utc) + timedelta(hours=3)).timestamp()
        }
        build_spec_to_cloud = BuildSpecToCloud(cyber_arena_spec=build_spec, debug=True)
        build_spec_to_cloud.commit()
        # fac = FixedArenaClass(build_id=build_spec['id'], debug=True)
        fac = FixedArenaClass(build_id='ppbblmcjub', debug=True)
        # fac.build()
        # fac.start()
        fac.stop()


if __name__ == "__main__":
    fixed_arena_class = 'stoc-class' if not fixed_arena_class else fixed_arena_class
    TestFixedArenaWorkout().build()