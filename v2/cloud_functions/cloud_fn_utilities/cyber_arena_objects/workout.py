from cloud_fn_utilities.gcp.cloud_env import CloudEnv
from cloud_fn_utilities.gcp.vpc_manager import VpcManager
from cloud_fn_utilities.gcp.datastore_manager import DataStoreManager
from cloud_fn_utilities.gcp.firewall_rule_manager import FirewallManager
from cloud_fn_utilities.gcp.pubsub_manager import PubSubManager
from cloud_fn_utilities.gcp.compute_manager import ComputeManager
from cloud_fn_utilities.gcp.cloud_logger import Logger
from cloud_fn_utilities.globals import DatastoreKeyTypes, PubSub, BuildConstants, WorkoutStates
from cloud_fn_utilities.state_managers.workout_states import WorkoutStateManager
from cloud_fn_utilities.server_specific.display_proxy import DisplayProxy

__author__ = "Philip Huff"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class Workout:
    def __init__(self, build_id, debug=False):
        self.workout_id = build_id
        self.debug = debug
        self.env = CloudEnv()
        self.logger = Logger("cloud_functions.workout").logger
        self.s = WorkoutStates
        self.pubsub_manager = PubSubManager(PubSub.Topics.CYBER_ARENA)
        self.state_manager = WorkoutStateManager(initial_build_id=self.workout_id)
        self.vpc_manager = VpcManager(build_id=self.workout_id)
        self.firewall_manager = FirewallManager()
        self.ds = DataStoreManager(key_type=DatastoreKeyTypes.WORKOUT, key_id=self.workout_id)
        self.workout = self.ds.get()
        if not self.workout:
            self.logger.error(f"The datastore record for {self.workout_id} no longer exists!")
            raise LookupError

    def build(self):
        if not self.workout.get('networks'):
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
                self.ds.put(server, key_type=DatastoreKeyTypes.SERVER, key_id=server_name)
                if self.debug:
                    ComputeManager(server_name=server_name).build()
                else:
                    self.pubsub_manager.msg(handler=str(PubSub.Handlers.BUILD.value),
                                            action=str(PubSub.BuildActions.SERVER.value), server_name=str(server_name))
            # Don't forget to build the Display Proxy Server!
            if self.debug:
                DisplayProxy(build_id=self.workout_id, build_spec=self.workout,
                             key_type=str(DatastoreKeyTypes.WORKOUT.value)).build()
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
        self.state_manager.state_transition(self.s.START)
        servers_to_start = self.ds.get_servers()

        for server in servers_to_start:
            server_name = server.key.name
            if self.debug:
                ComputeManager(server_name).start()
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

    def stop(self):
        self.state_manager.state_transition(self.s.STOPPING)
        servers_to_stop = self.ds.get_servers()

        for server in servers_to_stop:
            server_name = server.key.name
            if self.debug:
                ComputeManager(server_name).stop()
            else:
                self.pubsub_manager.msg(handler=PubSub.Handlers.CONTROL, action=str(PubSub.Actions.STOP.value),
                                        build_id=server_name,
                                        cyber_arena_object=str(PubSub.CyberArenaObjects.SERVER.value))

        if not self.state_manager.are_servers_stopped():
            self.state_manager.state_transition(self.s.BROKEN)
            self.logger.error(f"Workout {self.workout_id}: Timed out waiting for server builds to complete!")
        else:
            self.state_manager.state_transition(self.s.STOPPING)
            self.logger.info(f"Finished starting the Workout: {self.workout_id}!")

    def delete(self):
        self.state_manager.state_transition(self.s.DELETING_SERVERS)
        servers_to_delete = self.ds.get_servers()

        for server in servers_to_delete:
            server_name = server.key.name
            if self.debug:
                try:
                    ComputeManager(server_name=server_name).delete()
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
            self.logger.info(f"Finished deleting the Workout: {self.workout_id}!")
        else:
            self.state_manager.state_transition(self.s.BROKEN)
            self.logger.error(f"Workout {self.workout_id}: Timed out waiting for server deletions to complete!")

    def nuke(self):
        """

        Todo:
            This is copied over from fixed_arena_class and has not been touched

        Returns:

        """
        servers_to_nuke = self._get_servers(for_deletion=True)

        for server in servers_to_nuke:
            if self.debug:
                try:
                    ComputeManager(server).nuke()
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
