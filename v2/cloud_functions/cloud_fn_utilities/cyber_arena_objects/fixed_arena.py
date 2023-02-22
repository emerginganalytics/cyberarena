import logging
import time

from google.cloud import logging_v2

from cloud_fn_utilities.gcp.cloud_env import CloudEnv
from cloud_fn_utilities.gcp.vpc_manager import VpcManager
from cloud_fn_utilities.gcp.datastore_manager import DataStoreManager
from cloud_fn_utilities.gcp.firewall_rule_manager import FirewallManager
from cloud_fn_utilities.gcp.pubsub_manager import PubSubManager
from cloud_fn_utilities.gcp.compute_manager import ComputeManager
from cloud_fn_utilities.globals import DatastoreKeyTypes, PubSub, BuildConstants
from cloud_fn_utilities.state_managers.fixed_arena_states import FixedArenaStateManager
from cloud_fn_utilities.server_specific.firewall_server import FirewallServer
from cloud_fn_utilities.server_specific.display_proxy import DisplayProxy
from cloud_fn_utilities.cyber_arena_objects.fixed_arena_class import FixedArenaClass

__author__ = "Philip Huff"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff", "Ryan Ebsen", "Bryce Ebsen"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Production"


class FixedArena:
    def __init__(self, build_id, debug=False, env_dict=None):
        self.fixed_arena_id = build_id
        self.debug = debug
        self.env = CloudEnv(env_dict=env_dict) if env_dict else CloudEnv()
        self.env_dict = self.env.get_env()
        log_client = logging_v2.Client()
        log_client.setup_logging()
        self.s = FixedArenaStateManager.States
        self.pubsub_manager = PubSubManager(PubSub.Topics.CYBER_ARENA, env_dict=self.env_dict)
        self.state_manager = FixedArenaStateManager(initial_build_id=self.fixed_arena_id)
        self.vpc_manager = VpcManager(build_id=self.fixed_arena_id, env_dict=self.env_dict)
        self.firewall_manager = FirewallManager(env_dict=self.env_dict)
        self.ds = DataStoreManager(key_type=DatastoreKeyTypes.FIXED_ARENA, key_id=self.fixed_arena_id)
        self.fixed_arena = self.ds.get()
        if not self.fixed_arena:
            logging.error(f"The datastore record for {self.fixed_arena_id} no longer exists!")
            raise LookupError

    def build_fixed_arena(self):
        if not self.state_manager.get_state():
            self.state_manager.state_transition(self.s.START)

        if self.state_manager.get_state() < self.s.BUILDING_NETWORKS.value:
            self.state_manager.state_transition(self.s.BUILDING_NETWORKS)
            for network in self.fixed_arena['networks']:
                self.vpc_manager.build(network_spec=network)
            self.vpc_manager.build(network_spec=BuildConstants.Networks.GATEWAY_NETWORK_CONFIG)
            self.state_manager.state_transition(self.s.COMPLETED_NETWORKS)

        # Servers are built asynchronously and kicked off through pubsub messages.
        if self.state_manager.get_state() < self.s.BUILDING_SERVERS.value:
            self.state_manager.state_transition(self.s.BUILDING_SERVERS)
            for server in self.fixed_arena['servers']:
                server_name = f"{self.fixed_arena_id}-{server['name']}"
                server['parent_id'] = self.fixed_arena_id
                server['parent_build_type'] = self.fixed_arena['build_type']
                self.ds.put(server, key_type=DatastoreKeyTypes.SERVER, key_id=server_name)
                if self.debug:
                    ComputeManager(server_name=server_name, env_dict=self.env_dict).build()
                else:
                    self.pubsub_manager.msg(handler=str(PubSub.Handlers.BUILD.value),
                                            action=str(PubSub.BuildActions.SERVER.value), server_name=str(server_name))
            # Don't forget to build the Display Proxy Server!
            if self.debug:
                DisplayProxy(build_id=self.fixed_arena_id, build_spec=self.fixed_arena,
                             env_dict=self.env_dict).build()
            else:
                self.pubsub_manager.msg(handler=str(PubSub.Handlers.BUILD.value),
                                        action=str(PubSub.BuildActions.DISPLAY_PROXY.value),
                                        key_type=str(DatastoreKeyTypes.FIXED_ARENA.value),
                                        build_id=str(self.fixed_arena_id))

        if self.state_manager.get_state() < self.s.BUILDING_FIREWALL_RULES.value:
            self.state_manager.state_transition(self.s.BUILDING_FIREWALL_RULES)
            self.firewall_manager.build(self.fixed_arena_id, self.fixed_arena['firewall_rules'])
            self.state_manager.state_transition(self.s.COMPLETED_FIREWALL_RULES)

        if self.fixed_arena.get('firewalls', None) and self.state_manager.get_state() < self.s.BUILDING_FIREWALL.value:
            self.state_manager.state_transition(self.s.BUILDING_FIREWALL)
            FirewallServer(initial_build_id=self.fixed_arena_id, full_build_spec=self.fixed_arena,
                           env_dict=self.env_dict).build()
            self.state_manager.state_transition(self.s.COMPLETED_FIREWALL)

        if not self.state_manager.are_server_builds_finished():
            self.state_manager.state_transition(self.s.BROKEN)
            logging.error(f"Fixed Arena {self.fixed_arena_id}: Timed out waiting for server builds to complete!")
        else:
            self.state_manager.state_transition(self.s.READY)
            logging.info(f"Finished building Fixed Arena {self.fixed_arena_id}!")

    def delete_fixed_arena(self):
        logging.info(f"Deleting workout {self.fixed_arena_id}")
        if self.fixed_arena.get('firewalls', None):
            FirewallServer(initial_build_id=self.fixed_arena_id, full_build_spec=self.fixed_arena,
                           env_dict=self.env_dict).delete()
        self.firewall_manager.delete(self.fixed_arena_id)

        if self.debug:
            DisplayProxy(build_id=self.fixed_arena_id, build_spec=self.fixed_arena,
                         env_dict=self.env_dict).delete()
        else:
            self.pubsub_manager.msg(handler=str(PubSub.Handlers.MAINTENANCE.value),
                                    action=str(PubSub.Actions.DELETE.value),
                                    key_type=str(DatastoreKeyTypes.SERVER.value), build_id=self.fixed_arena_id)

        self.state_manager.state_transition(self.s.DELETING_SERVERS)
        active_class = self.fixed_arena.get('active_class', None)
        if active_class:
            if self.debug:
                FixedArenaClass(build_id=active_class, debug=self.debug, env_dict=self.env_dict).delete()
            else:
                self.pubsub_manager.msg(handler=str(PubSub.Handlers.CONTROL.value),
                                        action=str(PubSub.Actions.DELETE.value),
                                        key_type=str(DatastoreKeyTypes.FIXED_ARENA_CLASS.value), build_id=active_class)

        for server in self.fixed_arena['servers']:
            server_name = f'{self.fixed_arena_id}-{server["name"]}'
            if self.debug:
                ComputeManager(server_name=server_name, env_dict=self.env_dict).delete()
            else:
                self.pubsub_manager.msg(handler=str(PubSub.Handlers.CONTROL.value),
                                        action=str(PubSub.Actions.DELETE.value),
                                        key_type=str(DatastoreKeyTypes.SERVER.value), build_id=server_name)
        self.state_manager.state_transition(self.s.COMPLETED_DELETING_SERVERS)

        for network in self.fixed_arena['networks']:
            self.vpc_manager.delete(network_spec=network)
