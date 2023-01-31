import logging
from google.cloud import logging_v2

from cloud_fn_utilities.globals import PubSub, DatastoreKeyTypes
from cloud_fn_utilities.gcp.cloud_env import CloudEnv
from cloud_fn_utilities.gcp.datastore_manager import DataStoreManager
from cloud_fn_utilities.gcp.compute_manager import ComputeManager
from cloud_fn_utilities.server_specific.display_proxy import DisplayProxy
from cloud_fn_utilities.cyber_arena_objects.fixed_arena import FixedArena
from cloud_fn_utilities.cyber_arena_objects.fixed_arena_class import FixedArenaClass
from cloud_fn_utilities.server_specific.fixed_arena_workspace_proxy import FixedArenaWorkspaceProxy
from cloud_fn_utilities.cyber_arena_objects.unit import Unit
from cloud_fn_utilities.cyber_arena_objects.workout import Workout

from cloud_fn_utilities.gcp.pubsub_manager import PubSubManager

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
        action = self.event_attributes.get('action', None)
        if not action:
            logging.error(f"No action provided in cloud function build handler")
            raise ValueError
        if action == str(PubSub.BuildActions.FIXED_ARENA.value):
            build_id = self.event_attributes.get('build_id', None)
            if not build_id:
                logging.error(f"No build id provided for build handler with action {action}")
                raise ValueError
            FixedArena(build_id=build_id).build_fixed_arena()
        elif action == str(PubSub.BuildActions.FIXED_ARENA_CLASS.value):
            build_id = self.event_attributes.get('build_id', None)
            if not build_id:
                logging.error(f"No build id provided for build handler with action {action}")
                raise ValueError
            FixedArenaClass(build_id=build_id).build()
        elif action == str(PubSub.BuildActions.UNIT.value):
            build_id = self.event_attributes.get('build_id', None)
            if not build_id:
                logging.error(f"No build id provided for build handler with action {action}")
                raise ValueError
            Unit(build_id=build_id).build()
        elif action == str(PubSub.BuildActions.SERVER.value):
            server_name = self.event_attributes.get('server_name', None)
            if not server_name:
                logging.error(f"No server_name variable provided for the build handler with action {action}")
                raise ValueError
            ComputeManager(server_name=server_name).build()
        elif action == str(PubSub.BuildActions.DISPLAY_PROXY.value):
            key_type = self.event_attributes.get('key_type', None)
            build_id = self.event_attributes.get('build_id', None)
            if not key_type:
                logging.error(f"No key_type provided for the build handler with action "
                              f"BUILD_DISPLAY_PROXY")
                raise ValueError
            if not build_id:
                logging.error(f"No build_id provided for the build handler with action "
                              f"BUILD_DISPLAY_PROXY")
                raise ValueError
            if key_type in [DatastoreKeyTypes.FIXED_ARENA, DatastoreKeyTypes.WORKOUT]:
                build_spec = DataStoreManager(key_type=key_type, key_id=build_id).get()
            else:
                logging.error(f"Unsupported key type {key_type} supplied to build handler")
                raise ValueError
            DisplayProxy(build_id=build_id, build_spec=build_spec, key_type=key_type).build()
        elif action == str(PubSub.BuildActions.FIXED_ARENA_WORKSPACE_PROXY.value):
            build_id = self.event_attributes.get('build_id', None)
            workspace_ids = self.event_attributes.get('workspace_ids', None)
            if not build_id:
                logging.error(f"No build_id provided for the build handler with action "
                              f"BUILD_DISPLAY_PROXY")
                raise ValueError
            FixedArenaWorkspaceProxy(build_id=build_id, workspace_ids=workspace_ids.split()).build()
        else:
            logging.error(f"Unsupported action {action} supplied to build handler")
            raise ValueError

