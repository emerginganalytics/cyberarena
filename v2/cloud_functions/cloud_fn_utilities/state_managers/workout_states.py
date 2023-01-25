import time
from datetime import datetime
from enum import Enum, EnumMeta

from cloud_fn_utilities.gcp.datastore_manager import DataStoreManager
from cloud_fn_utilities.globals import DatastoreKeyTypes, ServerStates
from cloud_fn_utilities.gcp.cloud_logger import Logger
from cloud_fn_utilities.globals import WorkoutStates

__author__ = "Philip Huff"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class WorkoutStateManager:
    COMPLETION_STATES = [WorkoutStates.COMPLETED_DELETING_SERVERS.value, WorkoutStates.COMPLETED_FIREWALL.value,
                         WorkoutStates.COMPLETED_NETWORKS.value, WorkoutStates.COMPLETED_ROUTES.value,
                         WorkoutStates.COMPLETED_SERVERS.value, WorkoutStates.COMPLETED_STUDENT_ENTRY.value]
    OTHER_VALID_TRANSITIONS = [
        (WorkoutStates.READY.value, WorkoutStates.START.value),
        (WorkoutStates.READY.value, WorkoutStates.STARTING.value),
        (WorkoutStates.START.value, WorkoutStates.DELETING_SERVERS.value),
        (WorkoutStates.START.value, WorkoutStates.BUILDING_NETWORKS.value),
        (WorkoutStates.START.value, WorkoutStates.STARTING.value),
        (WorkoutStates.STARTING.value, WorkoutStates.RUNNING.value),
        (WorkoutStates.COMPLETED_NETWORKS.value, WorkoutStates.BUILDING_SERVERS.value),
        (WorkoutStates.BUILDING_SERVERS.value, WorkoutStates.BUILDING_FIREWALL_RULES.value),
        (WorkoutStates.BUILDING_FIREWALL_RULES.value, WorkoutStates.COMPLETED_FIREWALL_RULES.value),
        (WorkoutStates.RUNNING.value, WorkoutStates.STOPPING.value),
        (WorkoutStates.STOPPING.value, WorkoutStates.READY.value),
    ]

    MAX_WAIT_TIME = 300
    SLEEP_TIME = 10

    def __init__(self, initial_build_id=None):
        self.s = WorkoutStates
        self.server_states = ServerStates
        self.logger = Logger("cloud_functions.workout_states").logger
        if initial_build_id:
            self.ds = DataStoreManager(key_type=DatastoreKeyTypes.WORKOUT, key_id=initial_build_id)
            self.build = self.ds.get()
            if 'state' not in self.build:
                self.build['state'] = self.s.START.value
                self.build['state-timestamp'] = datetime.utcnow().isoformat()
                self.ds.put(self.build)
            self.build_id = initial_build_id
        else:
            self.ds = None
            self.build = None
            self.build_id = None

    def set_build_record(self, build_id):
        self.ds = DataStoreManager(key_type=DatastoreKeyTypes.WORKOUT, key_id=build_id)
        self.build = self.ds.get()
        if 'state' not in self.build:
            self.build['state'] = self.s.START.value
            self.build['state-timestamp'] = datetime.utcnow().isoformat()
            self.ds.put(self.build)

    def state_transition(self, new_state):
        """
        Consistently changes a datastore entity with the necessary state checks.
        :param entity: A datastore entity
        :param new_state: The new state for the server
        :return: Boolean on success. If the state transition is valid, then return True. Otherwise, return False
        """
        self.build = self.ds.get()
        new_state = new_state.value if type(new_state) != int else new_state
        existing_state = self.build['state']
        self.build['state'] = new_state
        self.build['state-timestamp'] = datetime.utcnow().isoformat()
        if self._is_valid_transition(existing_state, new_state):
            if new_state == WorkoutStates.DELETED:
                self.build['active'] = False
            elif new_state == WorkoutStates.READY:
                self.build['active'] = True
            self.logger.info(f"State Transition {self.build.key.name}: Transitioning from "
                             f"{self.s(existing_state).name} to {self.s(new_state).name}")
            self.ds.put(self.build)
            return True
        else:
            # TODO: Evaluate state transition errors
            self.ds.put(self.build)
            return False

    def get_state(self):
        return self.build['state']

    def get_state_timestamp(self):
        return self.build['state-timestamp']

    def are_server_builds_finished(self):
        max_wait_time = 300
        sleep_time = 10
        wait_time = 0
        servers_finished = False
        while not servers_finished and wait_time < max_wait_time:
            servers_finished = True
            servers = self.ds.get_servers()
            for server in servers:
                if server.get('state', None) != self.server_states.STOPPED.value:
                    servers_finished = False
            if not servers_finished:
                time.sleep(sleep_time)
                wait_time += sleep_time
        if servers_finished:
            return True
        else:
            return False

    def are_servers_started(self):
        return self._server_state_check(server_states=[self.server_states.RUNNING.value])

    def are_servers_stopped(self):
        return self._server_state_check(server_states=[self.server_states.STOPPED.value,
                                                       self.server_states.BROKEN.value])

    def are_servers_deleted(self):
        return self._server_state_check(server_states=[self.server_states.DELETED.value,
                                                       self.server_states.BROKEN.value])

    @staticmethod
    def get_expired():
        """
        This function returns a list of fixed_arena classes which have expired.
        @return: List of IDs for retired classes
        @rtype: list
        """
        return DataStoreManager(key_type=DatastoreKeyTypes.FIXED_ARENA_CLASS).get_expired()

    @staticmethod
    def get_running():
        """
        This function returns a list of fixed_arena classes which have expired.
        @return: List of IDs for retired classes
        @rtype: list
        """
        return DataStoreManager(key_type=DatastoreKeyTypes.SERVER).get_running()

    def _is_valid_transition(self, existing_state, new_state):
        if new_state == self.s.START.value:
            return True
        elif new_state == self.s.BUILDING_NETWORKS.value and existing_state in \
                [self.s.START.value, self.s.BROKEN.value, self.s.BUILDING_NETWORKS.value]:
            return True
        elif new_state == self.s.BUILDING_SERVERS.value and existing_state in \
                [self.s.COMPLETED_NETWORKS.value, self.s.BUILDING_SERVERS.value]:
            return True
        elif new_state == self.s.BUILDING_ROUTES.value and existing_state in \
                [self.s.COMPLETED_SERVERS.value, self.s.BUILDING_ROUTES.value]:
            return True
        elif new_state == self.s.BUILDING_FIREWALL.value and \
                existing_state in [self.s.COMPLETED_ROUTES.value, self.s.COMPLETED_SERVERS.value,
                                   self.s.COMPLETED_NETWORKS.value, self.s.BUILDING_FIREWALL.value]:
            return True
        elif new_state == self.s.READY.value and existing_state in [self.s.COMPLETED_SERVERS.value,
                                                                    self.s.COMPLETED_FIREWALL_RULES.value]:
            return True
        elif new_state in self.COMPLETION_STATES and existing_state \
                not in [self.s.DELETED.value, self.s.BROKEN.value]:
            return True
        elif new_state == self.s.DELETING_SERVERS.value and existing_state in [self.s.READY.value, self.s.RUNNING.value]:
            return True
        elif (existing_state, new_state) in self.OTHER_VALID_TRANSITIONS:
            return True
        else:
            self.logger.warning(f"Invalid build state transition! Attempting to move to {self.s(new_state).name}, but "
                                f"the build is currently in the state {self.s(existing_state).name}")
            return False

    def _server_state_check(self, server_states):
        wait_time = 0
        check_complete = False
        workspaces = self.ds.get_children(child_key_type=DatastoreKeyTypes.FIXED_ARENA_WORKSPACE,
                                          parent_id=self.build_id)
        while not check_complete and wait_time < self.MAX_WAIT_TIME:
            check_complete = True
            servers = self.ds.get_servers()
            for server in servers:
                if server.get('state', None) not in server_states:
                    check_complete = False
                    continue
            if not check_complete:
                time.sleep(self.SLEEP_TIME)
                wait_time += self.SLEEP_TIME
        if check_complete:
            return True
        else:
            return False
