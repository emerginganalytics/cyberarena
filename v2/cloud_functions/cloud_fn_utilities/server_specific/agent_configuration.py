import logging
from google.cloud import logging_v2
from cloud_fn_utilities.globals import BuildConstants
from cloud_fn_utilities.gcp.cloud_env import CloudEnv
from cloud_fn_utilities.gcp.pubsub_manager import PubSubManager

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

    agent_build_obj = {
        parent_id,
        parent_build_type,
        build_id => workout or workspace id that the agent is associated with
        agent_topic,
        agent_telemetry
    }
    """

    def __init__(self, build_id=None, parent_id=None, debug=False):
        log_client = logging_v2.Client()
        log_client.setup_logging()
        self.build_id = build_id
        self.env = CloudEnv()
        self.debug = debug

        # parent_id refers to either the fixed_arena_class or cyberarena_unit
        self.parent_id = parent_id
        self.build_type = BuildConstants.BuildType.FIXED_ARENA_WORKSPACE.value
        self.agent_topic = f"{self.parent_id}-agency"
        self.agent_subscription = f'{self.parent_id}-subscription'
        # self.agent_telemetry = PubSub.Topics.AGENT_TELEMETRY.value

    def create_topics(self):
        logging.info(f'Creating topic/subscription for agent with ID: {self.agent_topic}')
        PubSubManager(topic=self.agent_topic).create_topic()
        PubSubManager(topic=self.agent_topic).create_subscription(self.agent_subscription)
        # PubSubManager(topic=self.agent_telemetry).create_topic()

    def delete(self):
        """
        Expects parent_id (fixed-arena-class or unit) and delete the agent topic for each
        associated child

        Since each agent is treated like a workspace/workout server,
        we only need to worry about cleaning up the topics
        """
        logging.info(f'Deleting Agency Subscription: {self.agent_subscription}')
        PubSubManager(topic=self.agent_topic).delete_subscription(self.agent_subscription)
        logging.info(f'Deleting Agency Topic: {self.agent_topic}')
        PubSubManager(topic=self.agent_topic).delete_topic()

    def config(self):
        """
        Takes build_id for fixed-arena-class or cybergym-unit and creates agent machines and pubsub topics
        :return:
        """
        # Build the startup script
        startup_script = AttackerStartup.agent_start_env.format(
            agent_topic=self.agent_topic,
            build_id=self.build_id,
            build_type=self.build_type,
            telemetry_url=f'{self.env.main_app_url}/api/agency/telemetry/',
            agent_subscription=self.agent_subscription,
            project=self.env.project,
        )

        # Setup server config
        agent_config = {
            'build_type': BuildConstants.BuildType.AGENT_SERVER.value,
            'parent_id': self.build_id,
            'name': 'agent',
            'image': BuildConstants.MachineImages.AGENT,
            'machine_type': BuildConstants.MachineTypes.SMALL.value,
            'tags': {
                'items': ['allow-all-local-external']
            },
            'metadata': {'key': 'startup-script', 'value': startup_script},
            'nics': [],
            'serviceAccounts': [{
                'email': f'{self.env.project_number}-compute@developer.gserviceaccount.com',
                'scopes': [
                    'https://www.googleapis.com/auth/pubsub',
                    'https://www.googleapis.com/auth/devstorage.read_write',
                    'https://www.googleapis.com/auth/logging.write',
                    'https://www.googleapis.com/auth/cloudruntimeconfig'
                ]
            }]
        }
        return agent_config


class AttackerStartup:
    agent_start_env = \
        '#! /bin/bash\n' \
        'cat >> /etc/environment << EOF\n' \
        'AGENT_TOPIC={agent_topic}\n' \
        'BUILD_ID={build_id}\n' \
        'BUILD_TYPE={build_type}\n' \
        'TELEMETRY_URL={telemetry_url}\n' \
        'AGENT_SUBSCRIPTION={agent_subscription}\n' \
        'PROJECT={project}\n' \
        'EOF'

# [ eof ]
