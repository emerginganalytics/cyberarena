import logging
import pytz
from calendar import calendar
from datetime import datetime, timedelta
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
        self.env = CloudEnv(env_dict=env_dict) if env_dict else CloudEnv()
        self.env_dict = self.env.get_env()
        log_client = logging_v2.Client()
        log_client.setup_logging()
        now = self._get_localized_time()
        self.daily = self.hourly = self.quarter_hourly = False

        if self._is_midnight(now):
            self.daily = True
            self.hourly = True
            self.quarter_hourly = True
        elif 12 <= now.minute <= 18:
            self.hourly = True
            self.quarter_hourly = True
        elif (27 <= now.minute <= 33) or (42 <= now.minute <= 48):
            self.quarter_hourly = True

        print(f'Maintenance called at {now} for timezone {self._get_timezone()}')

    def route(self):
        logging.info(f'{self.daily} : {self.hourly} : {self.quarter_hourly}')
        if self.quarter_hourly:
            logging.info(f"Running quarter hourly maintenance tasks")
            QuarterHourlyMaintenance(env_dict=self.env_dict).run()

        if self.hourly:
            logging.info(f"Running hourly maintenance tasks")
            HourlyMaintenance(env_dict=self.env_dict).run()

        if self.daily:
            logging.info(f"Running daily maintenance tasks")
            DailyMaintenance(env_dict=self.env_dict).run()

    def _is_midnight(self, now):
        midnight = datetime(now.year, now.month, now.day, 0, 0, tzinfo=self._get_timezone())
        start = midnight - timedelta(minutes=5)
        end = midnight + timedelta(minutes=15)
        if start <= now <= end:
            return True
        return False

    def _get_localized_time(self):
        now = datetime.now(pytz.utc)
        timezone = self._get_timezone()
        return now.astimezone(timezone)

    def _get_timezone(self):
        return pytz.timezone(self.env.timezone)
