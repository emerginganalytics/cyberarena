from cloud_fn_utilities.gcp.pubsub_manager import PubSubManager
from cloud_fn_utilities.globals import PubSub
from cloud_fn_utilities.gcp.compute_manager import ProjectComputeManager
from cloud_fn_utilities.gcp.cloud_env import CloudEnv

from cloud_fn_utilities.database.vulnerabilities import Vulnerabilities


__author__ = "Philip Huff"
__copyright__ = "Copyright 2023, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff, Ryan Ebsen, Bryce Ebsen"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Production"


class DailyMaintenance:
    def __init__(self, debug=False):
        self.compute_manager = ProjectComputeManager()
        self.debug = debug
        self.pub_sub_mgr = PubSubManager(PubSub.Topics.CYBER_ARENA)
        self.env = CloudEnv()

    def run(self):
        self._stop_all()
        if self.env.sql_ip:
            Vulnerabilities().nvd_update()

    def _stop_all(self):
        self.compute_manager.stop_everything()
