import logging
import random
import string
from datetime import datetime
from netaddr import IPNetwork, IPAddress, iter_iprange

from google.cloud import logging_v2

from cloud_fn_utilities.gcp.cloud_env import CloudEnv
from cloud_fn_utilities.gcp.vpc_manager import VpcManager
from cloud_fn_utilities.gcp.datastore_manager import DataStoreManager
from cloud_fn_utilities.gcp.firewall_rule_manager import FirewallManager
from cloud_fn_utilities.gcp.pubsub_manager import PubSubManager
from cloud_fn_utilities.gcp.compute_manager import ComputeManager
from cloud_fn_utilities.globals import DatastoreKeyTypes, PubSub, BuildConstants
from cloud_fn_utilities.state_managers.fixed_arena_workout_states import FixedArenaWorkoutStateManager
from cloud_fn_utilities.server_specific.firewall_server import FirewallServer
from cloud_fn_utilities.server_specific.fixed_arena_workspace_proxy import FixedArenaWorkspaceProxy

__author__ = "Philip Huff"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class FixedArenaWorkoutBuild:
    def __init__(self, build_id, debug=False):
        self.fixed_arena_workout_id = build_id
        self.debug = debug
        self.env = CloudEnv()
        log_client = logging_v2.Client()
        log_client.setup_logging()
        self.s = FixedArenaWorkoutStateManager.States
        self.pubsub_manager = PubSubManager(PubSub.Topics.CYBER_ARENA)
        self.state_manager = FixedArenaWorkoutStateManager(initial_build_id=self.fixed_arena_workout_id)
        self.firewall_manager = FirewallManager()

        self.ds = DataStoreManager(key_type=DatastoreKeyTypes.FIXED_ARENA_WORKOUT, key_id=self.fixed_arena_workout_id)
        self.fixed_arena_workout = self.ds.get()
        if not self.fixed_arena_workout:
            logging.error(f"The datastore record for {self.fixed_arena_workout_id} no longer exists!")
            raise LookupError
        self.fixed_arena_workstations_ids = []
        ip_range = BuildConstants.Networks.Reservations.FIXED_ARENA_WORKOUT_SERVER_RANGE
        self.ip_reservations = list(iter_iprange(ip_range[0], ip_range[1]))
        self.next_reservation = 0

    def build(self):
        if not self.state_manager.get_state():
            self.state_manager.state_transition(self.s.START)

        # Create datastore records for each workspace under the key type fixed-arena-workout
        self.fixed_arena_workspace_ids = self._create_workspace_records()

        # Build workspace servers
        if self.state_manager.get_state() <= self.s.BUILDING_WORKSPACE_SERVERS.value:
            self.state_manager.state_transition(self.s.BUILDING_WORKSPACE_SERVERS)
            for ws_id in self.fixed_arena_workspace_ids:
                ws_servers = []
                for server in self.fixed_arena_workout['workspace_servers']:
                    server_name = f"{ws_id}-{server['name']}"
                    server['parent_id'] = ws_id
                    server['parent_build_type'] = self.fixed_arena_workout['build_type']
                    server['grandparent_id'] = self.fixed_arena_workout_id
                    server['great_grandparent_id'] = self.fixed_arena_workout['parent_id']
                    if 'nics' not in server:
                        server['nics'] = self._get_workspace_network_config()
                    self.ds.put(server, key_type=DatastoreKeyTypes.SERVER, key_id=server_name)
                    if self.debug:
                        ComputeManager(server_name=server_name).build()
                    else:
                        self.pubsub_manager.msg(handler=PubSub.Handlers.BUILD, action=PubSub.BuildActions.SERVER,
                                                server_name=server_name)
                    ws_servers.append(server)
                # Store the server information with IP addresses back with each fixed arena workout before looping
                ws_record = self.ds.get(key_type=DatastoreKeyTypes.FIXED_ARENA_WORKOUT, key_id=ws_id)
                ws_record['servers'] = ws_servers
                self.ds.put(ws_record, key_type=DatastoreKeyTypes.FIXED_ARENA_WORKOUT, key_id=ws_id)

            # Now build the Workspace Proxy Server
            if self.state_manager.get_state() <= self.s.BUILDING_WORKSPACE_PROXY.value:
                self.state_manager.state_transition(self.s.BUILDING_WORKSPACE_PROXY)
                if self.debug:
                    FixedArenaWorkspaceProxy(build_id=self.fixed_arena_workout_id,
                                             workspace_ids=self.fixed_arena_workspace_ids).build()
                else:
                    self.pubsub_manager.msg(handler=PubSub.Handlers.BUILD, action=PubSub.BuildActions.DISPLAY_PROXY,
                                            build_id=self.fixed_arena_workout_id,
                                            workspace_ids=self.fixed_arena_workspace_ids)

        if not self.state_manager.are_server_builds_finished(self.fixed_arena_workspace_ids):
            self.state_manager.state_transition(self.s.BROKEN)
            logging.error(f"Fixed Arena {self.fixed_arena_workout_id}: Timed out waiting for server builds to "
                          f"complete!")
        else:
            self.state_manager.state_transition(self.s.READY)
            logging.info(f"Finished building Fixed Arena {self.fixed_arena_workout_id}!")

    def start(self):
        self.state_manager.state_transition(self.s.START)
        display_proxy = f"{self.fixed_arena_workout_id}-{BuildConstants.Servers.FIXED_ARENA_WORKSPACE_PROXY}"
        servers_to_start = [display_proxy]
        for server in self.fixed_arena_workout['fixed_arena_servers']:
            self.fixed_arena_workout.get('fixed_arena_id')
            server_name = f"{self.fixed_arena_workout['parent_id']}-{server}"
            servers_to_start.append(server_name)
        for ws_id in self.fixed_arena_workout_id:
            ws_ds = DataStoreManager(key_type=DatastoreKeyTypes.FIXED_ARENA_WORKOUT, key_id=ws_id)
            ws_servers = ws_ds.get_servers()
            for ws_server in ws_servers:
                servers_to_start.append(ws_server)

        for server in servers_to_start:
            if self.debug:
                ComputeManager(server).start()
            else:
                self.pubsub_manager.msg(handler=PubSub.Handlers.MAINTENANCE,
                                        action=PubSub.MaintenanceActions.START_SERVER, server_name=server)

        if not self.state_manager.are_servers_started():
            self.state_manager.state_transition(self.s.BROKEN)
            logging.error(f"Fixed Arena {self.fixed_arena_workout_id}: Timed out waiting for server builds to "
                          f"complete!")
        else:
            self.state_manager.state_transition(self.s.RUNNING)
            logging.info(f"Finished starting the Fixed Arena Workout: {self.fixed_arena_workout_id}!")

    def stop(self):
        self.state_manager.state_transition(self.s.STOPPING)
        display_proxy = f"{self.fixed_arena_workout_id}-{BuildConstants.Servers.FIXED_ARENA_WORKSPACE_PROXY}"
        servers_to_stop = [display_proxy]
        for server in self.fixed_arena_workout['fixed_arena_servers']:
            self.fixed_arena_workout.get('fixed_arena_id')
            server_name = f"{self.fixed_arena_workout['parent_id']}-{server}"
            servers_to_stop.append(server_name)
        for ws_id in self.fixed_arena_workout_id:
            ws_ds = DataStoreManager(key_type=DatastoreKeyTypes.FIXED_ARENA_WORKOUT, key_id=ws_id)
            ws_servers = ws_ds.get_servers()
            for ws_server in ws_servers:
                servers_to_stop.append(ws_server)

        for server in servers_to_stop:
            if self.debug:
                ComputeManager(server).stop()
            else:
                self.pubsub_manager.msg(handler=PubSub.Handlers.MAINTENANCE,
                                        action=PubSub.MaintenanceActions.STOP_SERVER, server_name=server)

        if not self.state_manager.are_servers_stopped():
            self.state_manager.state_transition(self.s.BROKEN)
            logging.error(f"Fixed Arena {self.fixed_arena_workout_id}: Timed out waiting for server builds to "
                          f"complete!")
        else:
            self.state_manager.state_transition(self.s.STOPPING)
            logging.info(f"Finished stopping the Fixed Arena Workout: {self.fixed_arena_workout_id}!")

    def delete(self):
        self.state_manager.state_transition(self.s.DELETED)
        display_proxy = f"{self.fixed_arena_workout_id}-{BuildConstants.Servers.FIXED_ARENA_WORKSPACE_PROXY}"
        servers_to_delete = [display_proxy]
        for server in self.fixed_arena_workout['fixed_arena_servers']:
            self.fixed_arena_workout.get('fixed_arena_id')
            server_name = f"{self.fixed_arena_workout['parent_id']}-{server}"
            servers_to_delete.append(server_name)
        for ws_id in self.fixed_arena_workout_id:
            ws_ds = DataStoreManager(key_type=DatastoreKeyTypes.FIXED_ARENA_WORKOUT, key_id=ws_id)
            ws_servers = ws_ds.get_servers()
            for ws_server in ws_servers:
                servers_to_delete.append(ws_server)

        for server in servers_to_delete:
            if self.debug:
                ComputeManager(server).delete()
            else:
                self.pubsub_manager.msg(handler=PubSub.Handlers.MAINTENANCE,
                                        action=PubSub.MaintenanceActions.DELETE_SERVER, server_name=server)

        if not self.state_manager.are_servers_deleted():
            self.state_manager.state_transition(self.s.BROKEN)
            logging.error(f"Fixed Arena {self.fixed_arena_workout_id}: Timed out waiting for server builds to "
                          f"complete!")
        else:
            self.state_manager.state_transition(self.s.DELETED)
            logging.info(f"Finished deleting the Fixed Arena Workout: {self.fixed_arena_workout_id}!")

    def nuke(self):
        self.delete()
        print("I got here")
        self.build()
        print("I finished nuke")

    def _create_workspace_records(self):
        workspace_datastore = DataStoreManager()
        registration_required = self.fixed_arena_workout['workspace_settings'].get('registration_required', False)
        if registration_required:
            student_list = self.fixed_arena_workout['workspace_settings']['student_list']
            count = min(self.env.max_workspaces, len(student_list))
        else:
            count = min(self.env.max_workspaces, self.fixed_arena_workout['workspace_settings']['count'])

        workspace_ids = []
        for i in range(count):
            id = ''.join(random.choice(string.ascii_lowercase) for j in range(10))
            workspace_record = {
                'parent_id': self.fixed_arena_workout_id,
                'parent_build_type': self.fixed_arena_workout['build_type'],
                'build_type': BuildConstants.BuildType.FIXED_ARENA_WORKSPACE,
                'creation_timestamp': datetime.utcnow().isoformat(),
                'registration_required': registration_required,
            }
            if registration_required:
                workspace_record['workspace_email'] = student_list[i]
            workspace_datastore.put(workspace_record, key_type=DatastoreKeyTypes.FIXED_ARENA_WORKOUT, key_id=id)
            workspace_ids.append(id)
        return workspace_ids

    def _get_workspace_network_config(self):
        network_config = [{
            'network': BuildConstants.Networks.GATEWAY_NETWORK_NAME,
            'internal_ip': str(self.ip_reservations[self.next_reservation]),
            'subnet_name': 'default',
            'external_nat': False
        }]
        self.next_reservation += 1
        return network_config
