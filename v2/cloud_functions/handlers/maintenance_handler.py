import logging
from calendar import calendar
from datetime import time, datetime

import googleapiclient
from google import pubsub_v1
from google.cloud import logging_v2
from googleapiclient.errors import HttpError
from joblib import disk
from joblib.testing import timeout

from cloud_fn_utilities.gcp.datastore_manager import DataStoreManager
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

from cloud_fn_utilities.server_specific.fixed_arena_workspace_proxy import FixedArenaWorkspaceProxy
from cloud_fn_utilities.state_managers.fixed_arena_states import FixedArenaStateManager

#from cloud_fn_utilities.state_managers.server_states import ServerStateManag

from common.globals import log_client, compute, project, zone, LOG_LEVELS, ds_client, BUILD_STATES, PUBSUB_TOPICS, \
    WORKOUT_TYPES, cloud_log, workout_globals, SERVER_STATES, SERVER_ACTIONS, dns_suffix, parent_project, dnszone, \
    gcp_operation_wait
from common.state_transition import state_transition



class MaintenanceHandler:
    def __init__(self, event_attributes):
        self.state_manager = None
        self.server_name = event_attributes
        self.fixed_arena_workspace_ids = None
        self.env = CloudEnv()
        self.DEFAULT_LOOKBACK = 10512000
#        self.lookback_seconds = self.lookback_seconds
        log_client = logging_v2.Client()
        log_client.setup_logging()
        self.event_attributes = event_attributes
        #self.s = ServerStateManag.States
        self.server_spec = DataStoreManager(key_type=DatastoreKeyTypes.SERVER, key_id=self.event_attributes).get()
        self.compute = googleapiclient.discovery.build('compute', 'v1')
    #    self.server_states = ServerStateManag.States
        #self.lookback_seconds = self.lookback_seconds

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

