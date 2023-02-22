import logging
from calendar import calendar
from datetime import datetime
from google import pubsub_v1
from google.cloud import logging_v2
from cloud_fn_utilities.globals import PubSub, DatastoreKeyTypes, BuildConstants
from cloud_fn_utilities.gcp.cloud_env import CloudEnv
from cloud_fn_utilities.gcp.compute_manager import ComputeManager
from cloud_fn_utilities.gcp.pubsub_manager import PubSubManager
from cloud_fn_utilities.periodic_maintenance.hourly_maintenance import HourlyMaintenance
from cloud_fn_utilities.periodic_maintenance.quarter_hourly_maintenance import QuarterHourlyMaintenance
from cloud_fn_utilities.periodic_maintenance.daily_maintenance import DailyMaintenance


__author__ = "Philip Huff"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class MaintenanceHandler:
    def __init__(self, debug=False, env_dict=None):
        self.debug = debug
        self.env = CloudEnv(env_dict=env_dict)
        log_client = logging_v2.Client()
        log_client.setup_logging()
        now = datetime.now()
        self.daily = self.hourly = self.quarter_hourly = False
        if now.hour == 0 and now.minute <= 16:
            self.daily = True
            self.hourly = True
            self.quarter_hourly = True
        elif 12 <= now.minute <= 18:
            self.hourly = True
            self.quarter_hourly = True
        elif (27 <= now.minute <= 33) or (42 <= now.minute <= 48):
            self.quarter_hourly = True

    def route(self):
        if self.quarter_hourly:
            logging.info(f"Running quarter hourly maintenance tasks")
            QuarterHourlyMaintenance().run()

        if self.hourly:
            logging.info(f"Running hourly maintenance tasks")
            HourlyMaintenance().run()

        if self.daily:
            logging.info(f"Running daily maintenance tasks")
            DailyMaintenance().run()
