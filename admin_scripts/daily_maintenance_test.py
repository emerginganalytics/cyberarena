from v2.cloud_functions.cloud_fn_utilities.periodic_maintenance.daily_maintenance import DailyMaintenance
import yaml
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from v2.cloud_functions.cloud_fn_utilities.globals import Buckets
from v2.cloud_functions.cloud_fn_utilities.gcp.cloud_env import CloudEnv
from v2.main_app.main_app_utilities.gcp.bucket_manager import BucketManager
from v2.main_app.main_app_utilities.infrastructure_as_code.build_spec_to_cloud import BuildSpecToCloud
from cloud_fn_utilities.cyber_arena_objects.fixed_arena import FixedArena
from cloud_fn_utilities.gcp.pubsub_manager import PubSubManager
from cloud_fn_utilities.globals import PubSub, FixedArenaClassStates
from cloud_fn_utilities.state_managers.fixed_arena_states import FixedArenaStateManager

from cloud_fn_utilities.gcp.compute_manager import ComputeManager

__author__ = "Bryce Ebsen"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Bryce Ebsen"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "baebsen@ualr.edu"
__status__ = "Production"


class TestDailyMaintence:
    def __init__(self):
        self.env = CloudEnv()
        self.bm = BucketManager()
        self.pub_sub_mgr = PubSubManager(PubSub.Topics.CYBER_ARENA)
        self.fa_state_manager = FixedArenaStateManager()

    def build(self):
        test = DailyMaintenance(debug=True)
        test.run()


if __name__ == "__main__":
    # ComputeManager(server_name='cln-stoc-ad-domain-controler').start()
    # ComputeManager(server_name='cln-stoc-cln-firewall').start()
    TestDailyMaintence().build()
