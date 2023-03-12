import time

from cloud_fn_utilities.gcp.cloud_env import CloudEnv
from cloud_fn_utilities.gcp.vpc_manager import VpcManager
from cloud_fn_utilities.gcp.datastore_manager import DataStoreManager
from cloud_fn_utilities.gcp.firewall_rule_manager import FirewallManager
from cloud_fn_utilities.gcp.pubsub_manager import PubSubManager
from cloud_fn_utilities.gcp.compute_manager import ComputeManager
from cloud_fn_utilities.gcp.cloud_logger import Logger
from cloud_fn_utilities.globals import DatastoreKeyTypes, PubSub, BuildConstants, WorkoutStates, \
    get_current_timestamp_utc
from cloud_fn_utilities.state_managers.workout_states import WorkoutStateManager
from cloud_fn_utilities.server_specific.display_proxy import DisplayProxy

from datetime import datetime, timedelta, timezone

__author__ = "Philip Huff"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class Workout:
    def __init__(self, build_id, duration_hours=2, debug=False, env_dict=None):
        self.workout_id = build_id
        try:
            self.duration_seconds = min(int(duration_hours) * 3600, 36000) if duration_hours else 7200
        except ValueError:
            self.duration_seconds = 7200
        self.debug = debug
        self.env = CloudEnv(env_dict=env_dict) if env_dict else CloudEnv()
        self.env_dict = self.env.get_env()
        self.logger = Logger("cloud_functions.workout").logger
        self.s = WorkoutStates
        self.pubsub_manager = PubSubManager(PubSub.Topics.CYBER_ARENA, env_dict=self.env_dict)
        self.state_manager = WorkoutStateManager(initial_build_id=self.workout_id)
        self.vpc_manager = VpcManager(build_id=self.workout_id, env_dict=self.env_dict)
        self.firewall_manager = FirewallManager(env_dict=self.env_dict)
        self.ds = DataStoreManager(key_type=DatastoreKeyTypes.WORKOUT, key_id=self.workout_id)
        self.workout = self.ds.get()
        if not self.workout:
            self.logger.error(f"The datastore record for {self.workout_id} no longer exists!")
            raise LookupError

    def build(self):
        if not self.workout.get('networks', None):
            if self.workout.get('web_application', None):
                self.state_manager.state_transition(self.s.READY)
                self.logger.info(f"No compute assets required for workout {self.workout_id}.")
                self.logger.info(f"Finished building workout {self.workout_id}.")
            else:
                self.logger.info(f"No compute assets to build for workout {self.workout_id}.")
            return

        if not self.state_manager.get_state():
            self.state_manager.state_transition(self.s.START)

        if self.state_manager.get_state() < self.s.BUILDING_NETWORKS.value:
            self.state_manager.state_transition(self.s.BUILDING_NETWORKS)
            for network in self.workout['networks']:
                self.vpc_manager.build(network_spec=network)
            self.state_manager.state_transition(self.s.COMPLETED_NETWORKS)

        # Servers are built asynchronously and kicked off through pubsub messages.
        if self.state_manager.get_state() < self.s.BUILDING_SERVERS.value:
            self.state_manager.state_transition(self.s.BUILDING_SERVERS)
            for server in self.workout['servers']:
                server_name = f"{self.workout_id}-{server['name']}"
                server['parent_id'] = self.workout_id
                server['parent_build_type'] = self.workout['build_type']

                # Check for any custom DNS suffix
                dns_host_suffix = server['nics'][0].get('dns_host_suffix', None)
                if dns_host_suffix:
                    server['dns_hostname'] = f'{self.workout_id}-{dns_host_suffix}'
                self.ds.put(server, key_type=DatastoreKeyTypes.SERVER, key_id=server_name)
                if self.debug:
                    ComputeManager(server_name=server_name, env_dict=self.env_dict).build()
                else:
                    self.pubsub_manager.msg(handler=str(PubSub.Handlers.BUILD.value),
                                            action=str(PubSub.BuildActions.SERVER.value), server_name=str(server_name))
            # Don't forget to build the Display Proxy Server!
            if self.debug:
                DisplayProxy(build_id=self.workout_id, build_spec=self.workout,
                             key_type=str(DatastoreKeyTypes.WORKOUT.value), env_dict=self.env_dict).build()
            else:
                self.pubsub_manager.msg(handler=str(PubSub.Handlers.BUILD.value),
                                        action=str(PubSub.BuildActions.DISPLAY_PROXY.value),
                                        key_type=str(DatastoreKeyTypes.WORKOUT.value),
                                        build_id=str(self.workout_id))

        if self.state_manager.get_state() < self.s.BUILDING_FIREWALL_RULES.value:
            self.state_manager.state_transition(self.s.BUILDING_FIREWALL_RULES)
            self.firewall_manager.build(self.workout_id, self.workout['firewall_rules'])
            self.state_manager.state_transition(self.s.COMPLETED_FIREWALL_RULES)

        if not self.state_manager.are_server_builds_finished():
            self.state_manager.state_transition(self.s.BROKEN)
            self.logger.error(f"Workout {self.workout_id}: Timed out waiting for server builds to complete!")
        else:
            self.state_manager.state_transition(self.s.READY)
            self.logger.info(f"Finished building Workout {self.workout_id}!")

    def start(self):
        self.state_manager.state_transition(self.s.STARTING)
        servers_to_start = self.ds.get_servers()

        for server in servers_to_start:
            server_name = server.key.name
            if self.debug:
                ComputeManager(server_name, env_dict=self.env_dict).start()
            else:
                self.pubsub_manager.msg(handler=PubSub.Handlers.CONTROL, action=str(PubSub.Actions.START.value),
                                        build_id=server_name,
                                        cyber_arena_object=str(PubSub.CyberArenaObjects.SERVER.value))

        if not self.state_manager.are_servers_started():
            self.state_manager.state_transition(self.s.BROKEN)
            self.logger.error(f"Workout {self.workout_id}: Timed out waiting for server builds to complete!")
        else:
            self.state_manager.state_transition(self.s.RUNNING)
            self.logger.info(f"Finished starting the Workout: {self.workout_id}!")
        self.workout = self.ds.get()
        self.workout['shutoff_timestamp'] = get_current_timestamp_utc(add_seconds=self.duration_seconds)
        self.ds.put(self.workout)

    def stop(self):
        self.state_manager.state_transition(self.s.STOPPING)
        servers_to_stop = self.ds.get_servers()

        for server in servers_to_stop:
            server_name = server.key.name
            if self.debug:
                ComputeManager(server_name, env_dict=self.env_dict).stop()
            else:
                self.pubsub_manager.msg(handler=PubSub.Handlers.CONTROL, action=str(PubSub.Actions.STOP.value),
                                        build_id=server_name,
                                        cyber_arena_object=str(PubSub.CyberArenaObjects.SERVER.value))

        if not self.state_manager.are_servers_stopped():
            self.state_manager.state_transition(self.s.BROKEN)
            self.logger.error(f"Workout {self.workout_id}: Timed out waiting for server builds to stop!")
        else:
            self.state_manager.state_transition(self.s.READY)
            self.logger.info(f"Finished Stopping the Workout: {self.workout_id}!")
            self.workout = self.ds.get()
            self.workout['shutoff_timestamp'] = None
            self.ds.put(self.workout)

    def delete(self):
        self.state_manager.state_transition(self.s.DELETING_SERVERS)
        servers_to_delete = self.ds.get_servers()

        for server in servers_to_delete:
            server_name = server.key.name
            if self.debug:
                try:
                    ComputeManager(server_name=server_name, env_dict=self.env_dict).delete()
                except LookupError:
                    self.logger.error(f"Workout {self.workout_id}: Could not find server record for {server_name}. "
                                      f"Marking Workout record as broken.")
            else:
                self.pubsub_manager.msg(handler=PubSub.Handlers.CONTROL, action=str(PubSub.Actions.DELETE.value),
                                        build_id=server_name,
                                        cyber_arena_object=str(PubSub.CyberArenaObjects.SERVER.value))

        if self.state_manager.are_servers_deleted():
            for network in self.workout['networks']:
                self.vpc_manager.delete(network_spec=network)
            self.state_manager.state_transition(self.s.DELETED)
            self.logger.info(f"Finished deleting the Workout: {self.workout_id}!")
        else:
            self.state_manager.state_transition(self.s.BROKEN)
            self.logger.error(f"Workout {self.workout_id}: Timed out waiting for server deletions to complete!")

    def nuke(self):
        """
        Todo: This is copied over from fixed_arena_class and has not been touched
        Returns:
        """
        servers_to_nuke = self._get_servers(for_deletion=True)

        for server in servers_to_nuke:
            if self.debug:
                try:
                    ComputeManager(server, env_dict=self.env_dict).nuke()
                except LookupError:
                    continue
            else:
                self.pubsub_manager.msg(handler=PubSub.Handlers.CONTROL, action=str(PubSub.Actions.NUKE.value),
                                        build_id=server,
                                        cyber_arena_object=str(PubSub.CyberArenaObjects.SERVER.value))

        if not self.state_manager.are_server_builds_finished():
            self.state_manager.state_transition(self.s.BROKEN)
            self.logger.error(f"Fixed Arena {self.fixed_arena_class_id}: Timed out waiting for server builds to "
                              f"complete!")
        else:
            self.state_manager.state_transition(self.s.READY)
            self.logger.info(f"Finished nuking Fixed Arena {self.fixed_arena_class_id}!")

    def extend_runtime(self):
        shutoff_ts = self.workout.get('shutoff_timestamp', None)
        if shutoff_ts:
            self.workout['shutoff_timestamp'] = shutoff_ts + timedelta(seconds=self.duration_seconds)
            self.ds.put(self.workout)
