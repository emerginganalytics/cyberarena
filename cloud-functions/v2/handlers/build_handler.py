import logging
from google.cloud import logging_v2

from cloud_fn_utilities.globals import PubSub, DatastoreKeyTypes, BuildConstants
from cloud_fn_utilities.gcp.cloud_env import CloudEnv
from cloud_fn_utilities.gcp.datastore_manager import DataStoreManager
from cloud_fn_utilities.gcp.compute_manager import ComputeManager
from cloud_fn_utilities.server_specific.display_proxy import DisplayProxy
from cloud_fn_utilities.fixed_arena_build import FixedArenaBuild
from cloud_fn_utilities.fixed_arena_workout_build import FixedArenaWorkoutBuild
from cloud_fn_utilities.server_specific.fixed_arena_workspace_proxy import FixedArenaWorkspaceProxy

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
        if action == PubSub.BuildActions.FIXED_ARENA:
            build_id = self.event_attributes.get('build_id', None)
            if not build_id:
                logging.error(f"No build id provided for build handler with action {action}")
                raise ValueError
            FixedArenaBuild(build_id=build_id).build_fixed_arena()
        elif action == PubSub.BuildActions.FIXED_ARENA_WORKOUT:
            build_id = self.event_attributes.get('build_id', None)
            if not build_id:
                logging.error(f"No build id provided for build handler with action {action}")
                raise ValueError
            FixedArenaWorkoutBuild(build_id=build_id)
        elif action == PubSub.BuildActions.SERVER:
            server_name = self.event_attributes.get('server_name', None)
            if not server_name:
                logging.error(f"No server_name variable provided for the build handler with action {action}")
                raise ValueError
            ComputeManager(server_name=server_name).build()
        elif action == PubSub.BuildActions.DISPLAY_PROXY:
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
        elif action == PubSub.BuildActions.FIXED_ARENA_WORKSPACE_PROXY:
            build_id = self.event_attributes.get('build_id', None)
            workspace_ids = self.event_attributes.get('workspace_ids', None)
            FixedArenaWorkspaceProxy(build_id=build_id, workspace_ids=workspace_ids).build()
        else:
            logging.error(f"Unsupported action supplied to build handler")
            raise ValueError

