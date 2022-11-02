import logging
import time
from google.cloud import logging_v2
from cloud_fn_utilities.gcp.cloud_env import CloudEnv
from cloud_fn_utilities.gcp.datastore_manager import DataStoreManager
from cloud_fn_utilities.gcp.pubsub_manager import PubSubManager
from cloud_fn_utilities.gcp.compute_manager import ComputeManager
from cloud_fn_utilities.globals import DatastoreKeyTypes, PubSub, BuildConstants

__author__ = "Andrew Bomberger"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Andrew Bomberger",]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class CyberArenaAttacker:
    """
    Class to handle management of objects related specifically to the CLN red team network.
    build_id: workspace or workout id to attach agent machine to
    build_type_enum: Either enum type fixed-arena-class or cybergym-unit
    Agent: Red team entry point (attacker machine)

    """
    def __init__(self, build_id=None, parent_id=None):
        # log_client = logging_v2.Client()
        # log_client.setup_logging()
        self.build_id = build_id
        self.server_name = f'{self.build_id}-agent'
        self.env = CloudEnv()
        self.ds_manager = DataStoreManager()
        self.pubsub_manager = PubSubManager(PubSub.Topics.CYBER_ARENA)

        # Used only during topic creation/deletion
        self.parent_id = parent_id
        self.agent_topic = f'{self.parent_id}-botnet'
        self.agent_telemetry = PubSub.Topics.AGENT_TELEMETRY.value

    def config(self):
        """
        Takes build_id for fixed-arena-class or cybergym-unit and creates agent machines and pubsub topics
        :return:
        """
        startup_script = AttackerStartup.agent_start_env.format(
            self.agent_topic, self.agent_telemetry, self.server_name)

        # Setup server config
        agent_config = {
            'build_type': BuildConstants.BuildType.FIXED_ARENA_WORKSPACE,
            'parent_id': self.build_id,
            'name': self.server_name,
            'image': BuildConstants.MachineImages.AGENT,
            'machine_type': BuildConstants.MachineTypes.SMALL,
            'tags': {
                'items': ['allow-all-local-external']
            },
            'metadata': {'key': 'startup-script', 'value': startup_script},
            'nics': [{
                'network': 'enterprise',
                'internal_ip': BuildConstants.Networks.Reservations.AGENT_SERVER,
                'subnet_name': 'default',
                'external_nat': False
                }
            ],
        }
        return agent_config

    def create_topics(self):
        PubSubManager(topic=self.agent_topic).create_topic()
        PubSubManager(topic=self.agent_telemetry).create_topic()

    def delete(self):
        """
        Expects parent_id (fixed-arena-class or unit) and delete agents for each
        associated child
        """
        logging.info(f'Deleting Agency topic ...')
        PubSubManager(topic=f'{self.build_id}-botnet').delete_topic()


class AttackerStartup:
    agent_start_env = \
        '#! /bin/bash\n' \
        'cat >> /etc/environment << EOF\n' \
        'AGENT_TOPIC={agent_topic}\n' \
        'AGENT_TELEMETRY={agent_telemetry}\n' \
        'BUILD_ID={build_id}\n' \
        'EOF'

# [ eof ]
