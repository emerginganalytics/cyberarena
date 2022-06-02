import logging
from google.cloud import logging_v2

from cloud_fn_utilities.globals import PubSub, DatastoreKeyTypes, BuildConstants
from cloud_fn_utilities.gcp.cloud_env import CloudEnv
from cloud_fn_utilities.gcp.datastore_manager import DataStoreManager
from cloud_fn_utilities.gcp.compute_manager import ComputeManager
from cloud_fn_utilities.server_specific.display_proxy import DisplayProxy

__author__ = "Philip Huff"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class BuildHandler:
    def __init__(self, event_attributes):
        self.env = CloudEnv()
        log_client = logging_v2.Client()
        log_client.setup_logging()
        self.event_attributes = event_attributes

    def route(self):
        action = self.event_attributes('action', None)
        if not action:
            logging.error(f"No action provided in cloud function build handler")
            raise ValueError

        if action == PubSub.Actions.BUILD_SERVER:
            server_name = self.event_attributes.get('server_name', None)
            if not server_name:
                logging.error(f"No server_name variable provided for the build handler with action BUILD_SERVER")
                raise ValueError
            ComputeManager(server_name=server_name).build()
        elif action == PubSub.Actions.BUILD_DISPLAY_PROXY:
            key_type = self.event_attributes.get('key_type', None)
            build_id = self.event_attributes.get('key_id', None)
            if not key_type or not build_id:
                logging.error(f"No key_type or build_id provided for the build handler with action "
                              f"BUILD_DISPLAY_PROXY")
                raise ValueError
            if key_type == DatastoreKeyTypes.FIXED_ARENA:
                build_spec = DataStoreManager(key_type=key_type, key_id=build_id)
            else:
                logging.error(f"Unsupported key type supplied to build handler")
                raise ValueError
            DisplayProxy(build_id=build_id, build_spec=build_spec).build()
        else:
            logging.error(f"Unsupported action supplied to build handler")
            raise ValueError

