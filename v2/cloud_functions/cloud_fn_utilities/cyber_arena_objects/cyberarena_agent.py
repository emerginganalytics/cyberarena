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


class CyberArenaAgent:
    """
    Class to handle management of objects related specifically to the CLN red team network.
    build_id: workspace or workout id to attach agent machine to
    build_type_enum: Either enum type fixed-arena-class or cybergym-unit
    Agent: Red team entry point (attacker machine)
    """
    def __init__(self, build_id=None, parent_id=None):
        log_client = logging_v2.Client()
        log_client.setup_logging()
        self.build_id = build_id
        self.env = CloudEnv()
        self.ds_manager = DataStoreManager()
        self.pubsub_manager = PubSubManager(PubSub.Topics.CYBER_ARENA)

        # Used only during topic creation/deletion;
        # parent_id refers to either the fixed_arena_class or cyberarena_unit
        self.parent_id = parent_id
        self.build_type = BuildConstants.BuildType.FIXED_ARENA_WORKSPACE.value
        self.agent_topic = f"{self.parent_id}-agency"
        # self.agent_telemetry = PubSub.Topics.AGENT_TELEMETRY.value

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
            telemetry_url=f'{self.env.main_app_url}/api/agency/telemetry/'
        )
        # Setup server config
        agent_config = {
            'build_type': BuildConstants.BuildType.AGENT_SERVER.value,
            'parent_id': self.build_id,
            'name': f'{self.build_id}-agent',
            'image': BuildConstants.MachineImages.AGENT,
            'machine_type': BuildConstants.MachineTypes.SMALL.value,
            'tags': {
                'items': ['allow-all-local-external']
            },
            'metadata': {'key': 'startup-script', 'value': startup_script},
            'nics': [],
            'serviceAccounts': [{
                'email': f'{self.env.project_number}-compute@developer.gserviceaccount.com',
                'scopes': ['default', 'pubsub']
            }]
        }
        return agent_config

    def delete(self):
        """
        Expects parent_id (fixed-arena-class or unit) and delete the agent topic for each
        associated child

        Since each agent is treated like a workspace/workout server,
        we only need to worry about cleaning up the topics
        """
        logging.info(f'Deleting Agency topic')
        PubSubManager(topic=self.agent_topic).delete_topic()

    def send_command(self, event_attributes):
        action = event_attributes['action']
        build_type = event_attributes['build_type']
        if action == str(PubSub.BuildActions.ATTACK):
            if build_type == BuildConstants.BuildType.FIXED_ARENA_CLASS:
                check_topics = self._check_agency_topics()
                if check_topics:
                    workspaces = self.ds_manager.get_workspaces(key_type=DatastoreKeyTypes.FIXED_ARENA_WORKSPACE.value,
                                                                build_id=self.parent_id)
                    for workspace in workspaces:
                        w_id = workspace.key.name
                        PubSubManager(topic=str(PubSub.Topics.CYBER_ARENA.value)).msg(build_id=str(self.build_id),
                                      action=str(action), build_type=str(DatastoreKeyTypes.FIXED_ARENA_WORKSPACE))
                else:
                    print(f'No topics found for fixed_arena_class with id : {self.parent_id}')
            if build_type == BuildConstants.BuildType.FIXED_ARENA_WORKSPACE:
                attack_obj = self.ds_manager.get(key_type=DatastoreKeyTypes.CYBERARENA_ATTACK, key_id=self.build_id)
                server_name = attack_obj['args']['target_machine']
                attack_obj['args']['target_addr'] = self._get_target_ip(server_name=server_name)

                # Send attack msg to the Agent topic
                command = PubSubManager(topic=self.agent_topic).msg(build_id=self.build_id, attack_id=attack_obj['id'],
                                                                    attack_args=attack_obj['args'])

    def create_topics(self):
        logging.info(f'Creating Agent PubSub topics: {self.agent_topic}')
        PubSubManager(topic=self.agent_topic).create_topic()
        # PubSubManager(topic=self.agent_telemetry).create_topic()

    def _get_target_ip(self, server_name):
        servers = DataStoreManager(key_type=DatastoreKeyTypes.SERVER, key_id=self.build_id).get_servers()
        if servers:
            ip_addr = ''
            for server in servers:
                if server_name in server['nics'][0]['name']:
                    ip_addr = server['nics'][0].get('internal_ip')
                    return ip_addr
        raise ValueError(f'No server found with server_name={server_name} for CyberArenaAgent._get_target_ip')

    def _check_agency(self):
        """Returns True if topic and machines exist for requested Agency"""
        pass

    def _check_agency_topics(self):
        topic_names = [
            PubSubManager(topic=PubSub.Topics.AGENT_TELEMETRY.value).topic_path,
            PubSubManager(topic=self.agent_topic).topic_path
        ]
        found = []
        topic_list = PubSubManager(topic=PubSub.Topics.AGENT_TELEMETRY.value).list_topics()
        for topic in topic_list:
            if topic.name in topic_names:
                found.append(True)
        if len(found) == 2:
            return True
        return False


class AttackerStartup:
    agent_start_env = \
        '#! /bin/bash\n' \
        'cat >> /etc/environment << EOF\n' \
        'AGENT_TOPIC={agent_topic}\n' \
        'BUILD_ID={build_id}\n' \
        'BUILD_TYPE={build_type}\n' \
        'TELEMETRY_URL={telemetry_url}\n' \
        'EOF'

# [ eof ]
