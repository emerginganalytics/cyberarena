import logging
import time
from google.cloud import logging_v2
from cloud_fn_utilities.gcp.cloud_env import CloudEnv
from cloud_fn_utilities.gcp.datastore_manager import DataStoreManager
from cloud_fn_utilities.gcp.pubsub_manager import PubSubManager
from cloud_fn_utilities.gcp.compute_manager import ComputeManager
from cloud_fn_utilities.globals import DatastoreKeyTypes, PubSub, BuildConstants
from cloud_fn_utilities.state_managers.agency_states import AgencyStateManager
from cloud_fn_utilities.command_and_control.agent import Agent

__author__ = "Andrew Bomberger"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Andrew Bomberger",]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class Agency:
    """
    Class to handle management of objects related specifically to the CLN red team network.
    build_id: workspace or workout id to attach agent machine to
    Agent: Red team entry point (attacker machine)

    """
    def __init__(self, build_id, build_type=None, create_topic=False, debug=False):
        # log_client = logging_v2.Client()
        # log_client.setup_logging()
        self.build_id = build_id
        self.create_topic = create_topic
        self.debug = debug
        self.env = CloudEnv()
        self.states = AgencyStateManager.States
        self.pubsub_manager = PubSubManager(PubSub.Topics.CYBER_ARENA)
        self.state_manager = AgencyStateManager(initial_build_id=self.build_id)
        if build_type == BuildConstants.BuildType.FIXED_ARENA_WORKSPACE:
            self.key_type = DatastoreKeyTypes.FIXED_ARENA_WORKSPACE

    @staticmethod
    def get_server_name(build_id):
        return f'{build_id}-agent'

    def get_build_ds(self):
        ds = DataStoreManager(key_type=self.key_type, key_id=self.build_id)
        cyber_arena_build = ds.get()
        if not cyber_arena_build:
            # logging.error(f'The datastore record for {self.build_id} no longer exists!')
            print(f'The datastore record for {self.build_id} no longer exists!')
            raise LookupError
        return cyber_arena_build

    def build(self):
        """
        Takes build_id for fixed-arena-class and creates agent machine and pubsub topic
        :return:
        """
        build = self.get_build_ds()
        parent_id = build.get('parent_id', None)
        if not parent_id:
            raise AttributeError(f'Attribute parent_id does not exist in build, {self.build_id}')

        agent_obj = {
            'build_id': self.build_id,
            'server_name': self.get_server_name(self.build_id),
            'agent_topic': f'{parent_id}-botnet',
            'agent_telemetry': f'{self.build_id}-telemetry'
        }
        if not self.state_manager.get_state():
            self.state_manager.state_transition(self.states.START)
        if self.create_topic:
            if self.state_manager.get_state() < self.states.BUILDING_PUBSUB.value:
                # Agent telemetry is created on the fixed-arena-class or unit level and not the workspace level
                self.state_manager.state_transition(self.states.BUILDING_PUBSUB)
                PubSubManager(topic=agent_obj['topic_name']).create_topic()
            self.state_manager.state_transition(self.states.COMPLETED_PUBSUB)

        if self.state_manager.get_state() < self.states.BUILDING_AGENT.value:
            self.state_manager.state_transition(self.states.BUILDING_AGENT)
            # Add the server to the cybergym-server datastore obj
            Agent(agent_build_obj=agent_obj, build_type_enum=BuildConstants.BuildType.FIXED_ARENA_WORKSPACE,
                  debug=self.debug).commit_to_cloud()
            if self.debug:
                ComputeManager(server_name=agent_obj['server_name']).build()
            else:
                self.pubsub_manager.msg(handler=str(PubSub.Handlers.BUILD), action=str(PubSub.BuildActions.SERVER),
                                        server_name=str(agent_obj['server_name']))
            self.state_manager.state_transition(self.states.COMPLETED_AGENT)

    def delete(self):
        """
        Expects parent_id (fixed-arena-class or unit) and delete agents for each
        associated child
        """
        # logging.info(f'Deleting Agent {self.build_id}')
        # TODO: Add state checking logic
        cyber_arena_builds = DataStoreManager().get_workspaces(key_type=DatastoreKeyTypes.FIXED_ARENA_WORKSPACE,
                                                               build_id=self.build_id)
        for build in cyber_arena_builds:
            build_id = build.key.name
            server_name = self.get_server_name(build_id)
            if self.debug:
                ComputeManager(server_name=server_name).delete()
            else:
                # TODO: Does build_id refer to the build_id or the unique server_name?
                self.pubsub_manager.msg(handler=str(PubSub.Handlers.CONTROL.value),
                                        action=str(PubSub.Actions.DELETE.value),
                                        key_type=str(DatastoreKeyTypes.SERVER.value),
                                        build_id=server_name)

        # Finally delete the PubSub topics for this parent_build
        PubSubManager(topic=f'{self.build_id}-botnet').delete_topic()
        PubSubManager(topic=f'{self.build_id}-telemetry').delete_topic()

# [ eof ]
