# TODO: - Add logic to append server name to parent build datastore object.
#       - Determine if botnet_handler will handle all build requests for the agency or if
#           some workload will be offloaded through the build_handler instead.
#       - Validate state transition model is functioning properly
import time
import logging
from google.cloud import logging_v2
from cloud_fn_utilities.gcp.pubsub_manager import PubSubManager
from cloud_fn_utilities.gcp.compute_manager import ComputeManager
from cloud_fn_utilities.gcp.datastore_manager import DatastoreKeyTypes, DataStoreManager
from cloud_fn_utilities.globals import DatastoreKeyTypes, BuildConstants, PubSub
from cloud_fn_utilities.state_managers.agency_states import AgencyStateManager

__author__ = "Andrew Bomberger"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Andrew Bomberger"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class Agent(object):
    """
    Agents are the red team machines that are injected into the specified network to act as the
    main contact point in an emulated botnet.

    Build_id refers to the workout or workspace id that the agent is associated with.
    """
    def __init__(self, agent_build_obj, build_type_enum, debug=False):
        self.agent_build_obj = agent_build_obj
        self.build_id = self.agent_build_obj.get('build_id', None)
        self.server_name = f'{self.build_id}-agent'
        self.server_exists()
        self.build_type_enum = build_type_enum
        if self.build_type_enum == BuildConstants.BuildType.FIXED_ARENA_WORKSPACE:
            self.cyber_arena_build = self.get_workspace()
        elif self.build_type_enum == BuildConstants.BuildType.WORKOUT:
            self.cyber_arena_build = self.get_workout()
        self.startup_script = '#! /bin/bash\n' \
                              'cat >> /etc/environment << EOF\n' \
                              'AGENT_TOPIC={' + self.agent_build_obj["agent_topic"] + '}\n' \
                              'AGENT_TELEMETRY={' + self.agent_build_obj['agent_telemetry'] + '}\n' \
                              'EOF'
        self.debug = debug
        self.ds = DataStoreManager()
        # log_client = logging_v2.Client()
        # log_client.setup_logging()

    def server_exists(self):
        exists = DataStoreManager(key_type=DatastoreKeyTypes.SERVER, key_id=self.server_name).get()
        if exists:
            raise ValueError(f'Agent Operation Failed. Resource with name {self.server_name} already exists')
        return False

    def get_workspace(self):
        workspace = DataStoreManager(key_type=DatastoreKeyTypes.FIXED_ARENA_WORKSPACE, key_id=self.build_id).get()
        if not workspace:
            raise ValueError(f'No build exists with build_id {self.build_id}')
        return workspace

    def get_workout(self):
        # workout = DatastoreManager(key_type=DatastoreKeyTypes.WORKOUT, key_id=self.build_id).get()
        workout = {}
        if not workout:
            raise ValueError(f'No build exists with build_id {self.build_id}')
        return workout

    def commit_to_cloud(self):
        # Create server specification ds object
        machine_specs = {
            'parent_id': self.cyber_arena_build['parent_id'],
            'name': self.server_name,
            'image': BuildConstants.MachineImages.AGENT,
            'machine_type': BuildConstants.MachineTypes.SMALL,
            'tags': {'items': ['allow-all-local-external']},
            'metadata': self.startup_script,
            'nics': [
                {
                    'network': 'enterprise',
                    'internal_ip': BuildConstants.Networks.Reservations.AGENT_SERVER,
                    'subnet_name': 'default',
                    'external_nat': False
                }
            ],
            'build_type': BuildConstants.BuildType.AGENT,
        }

        # Push config to cybergym-server datastore and add server to list parent list of machines
        self.ds.put(machine_specs, key_type=DatastoreKeyTypes.SERVER, key_id=self.server_name)
        # TODO: Also add records to either fixed-arena-class or fixed-arena-workspace

        # Send PubSub request to Botnet Handler for server build
        if not self.debug:
            PubSubManager(topic=PubSub.Handlers.BOTNET.value).msg()
# [ eof ]
