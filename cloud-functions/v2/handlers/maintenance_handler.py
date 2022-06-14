import logging
from google.cloud import logging_v2

from cloud_fn_utilities.globals import PubSub, DatastoreKeyTypes, BuildConstants
from cloud_fn_utilities.gcp.cloud_env import CloudEnv
from cloud_fn_utilities.gcp.compute_manager import ComputeManager

__author__ = "Philip Huff"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class MaintenanceHandler:
    def __init__(self, event_attributes):
        self.env = CloudEnv()
        log_client = logging_v2.Client()
        log_client.setup_logging()
        self.event_attributes = event_attributes

    def route(self):
        action = self.event_attributes('action', None)
        if not action:
            logging.error(f"No action provided in cloud function maintenance handler")
            raise ValueError
        if action == PubSub.MaintenanceActions.START_SERVER:
            build_id = self.event_attributes.get('build_id', None)
            if not build_id:
                logging.error(f"No build id provided for maintenance handler with action {action}")
                raise ValueError
            ComputeManager(server_name=build_id).start()
        else:
            logging.error(f"Unsupported action supplied to the maintenance handler")
            raise ValueError

