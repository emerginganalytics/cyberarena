import yaml
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from v2.cloud_functions.cloud_fn_utilities.globals import Buckets
from v2.cloud_functions.cloud_fn_utilities.gcp.cloud_env import CloudEnv
from v2.main_app.main_app_utilities.gcp.bucket_manager import BucketManager
from v2.main_app.main_app_utilities.infrastructure_as_code.build_spec_to_cloud import BuildSpecToCloud
from cloud_fn_utilities.cyber_arena_objects.fixed_arena import FixedArena


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
fixed_arena = args.get('fixed_arena')


class TestFixedArena:
    def __init__(self):
        self.env = CloudEnv()
        self.bm = BucketManager()

    def build(self):
        fixed_arena_yaml = self.bm.get(bucket=self.env.spec_bucket, file=f"{Buckets.Folders.SPECS}{fixed_arena}.yaml")
        build_spec = yaml.safe_load(fixed_arena_yaml)
        build_spec_to_cloud = BuildSpecToCloud(cyber_arena_spec=build_spec, debug=True)
        build_spec_to_cloud.commit()
        fab = FixedArena(fixed_arena_id=build_spec['id'], debug=True)
        fab.build_fixed_arena()


if __name__ == "__main__":
    fixed_arena = 'stoc' if not fixed_arena else fixed_arena
    TestFixedArena().build()
