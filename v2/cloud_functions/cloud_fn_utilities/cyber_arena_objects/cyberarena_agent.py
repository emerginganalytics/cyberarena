import logging
import json
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
    Agent: Red team entry point (attacker machine)

    """
    def __init__(self, build_id=None, debug=False, env_dict=None):
        log_client = logging_v2.Client()
        log_client.setup_logging()
        self.build_id = build_id
        self.env = CloudEnv(env_dict=env_dict) if env_dict else CloudEnv()
        self.env_dict = self.env.get_env()
        self.ds_manager = DataStoreManager()
        self.pubsub_manager = PubSubManager(PubSub.Topics.CYBER_ARENA, env_dict=self.env_dict)
        self.debug = debug

    def send_command(self, event_attributes):
        action = event_attributes['action']
        build_type = event_attributes['build_type']
        attack_id = event_attributes['attack_id']
        if action == str(PubSub.BuildActions.CYBER_ARENA_ATTACK.value):
            # TODO: Call check for agency builds for class
            logging.info(f'BuildType {build_type} for action {action} in CyberArenaAgent')
            if build_type == str(BuildConstants.BuildType.FIXED_ARENA_CLASS.value):
                if self._check_agency_topics():
                    workspaces = self.ds_manager.get_workspaces(key_type=DatastoreKeyTypes.FIXED_ARENA_WORKSPACE.value, build_id=self.build_id)
                    for workspace in workspaces:
                        w_id = workspace.key.name
                        if not self.debug:
                            PubSubManager(topic=str(PubSub.Topics.CYBER_ARENA.value), env_dict=self.env_dict).msg(
                                handler=str(PubSub.Handlers.AGENCY.value), action=str(action),
                                attack_id=attack_id, build_id=str(w_id),
                                build_type=str(BuildConstants.BuildType.FIXED_ARENA_WORKSPACE.value)
                            )
                        else:
                            event_attr_copy = event_attributes.copy()
                            event_attr_copy['build_type'] = str(BuildConstants.BuildType.FIXED_ARENA_WORKSPACE.value)
                            CyberArenaAgent(build_id=w_id, debug=self.debug, env_dict=self.env_dict).send_command(event_attr_copy)
            if build_type == BuildConstants.BuildType.FIXED_ARENA_WORKSPACE:
                attack_obj = self.ds_manager.get(key_type=DatastoreKeyTypes.CYBERARENA_ATTACK, key_id=attack_id)
                agent_topic = attack_obj['topics']['commands']
                server_name = f"{self.build_id}-{attack_obj['args']['target_machine']}"
                attack_obj['args']['target_addr'] = self._get_target_ip(server_name=server_name)
                # Send attack msg to the Agent topic
                logging.info(f'Sending command ({attack_obj["id"]}: {attack_obj["module"]} to Agent {self.build_id}')
                if not self.debug:
                    command = PubSubManager(topic=agent_topic, env_dict=self.env_dict)\
                        .msg(build_id=str(self.build_id), attack_id=str(attack_obj['id']),
                                                                   args=str(json.dumps(attack_obj['args'])),
                                                                   module=str(attack_obj['module']))
                else:
                    print(f'{agent_topic} ==> BUILD_ID: {self.build_id}; ATTACK_ID: {attack_obj["id"]}; '
                          f'ARGS: {attack_obj["args"]}; MODULE: {attack_obj["module"]}')

    def _get_target_ip(self, server_name):
        servers = DataStoreManager(key_type=DatastoreKeyTypes.SERVER, key_id=self.build_id).get_servers()
        if servers:
            ip_addr = ''
            for server in servers:
                if server_name in server.key.name:
                    ip_addr = server['nics'][0].get('internal_ip')
                    return ip_addr
        logging.error(f'No server found with server_name={server_name} for CyberArenaAgent._get_target_ip')
        raise ValueError

    def _check_agency(self):
        # TODO: Add check for if agent topic and machines exist. Call before sending attack PubSub messages
        pass

    def _check_agency_topics(self):
        topic_names = [
            PubSubManager(topic=PubSub.Topics.AGENT_TELEMETRY.value, env_dict=self.env_dict).topic_path,
            PubSubManager(topic=f'{self.build_id}-agency', env_dict=self.env_dict).topic_path  # Ideally we don't hard code this value
        ]
        found = []
        topic_list = PubSubManager(topic=PubSub.Topics.AGENT_TELEMETRY.value, env_dict=self.env_dict).list_topics()
        found = []
        for topic in topic_list:
            if topic.name in topic_names:
                found.append(True)
        if len(found) == 2:
            return True
        return False

# [ eof ]
