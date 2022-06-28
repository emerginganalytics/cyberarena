import time
from datetime import datetime
from enum import Enum
import logging

from cloud_fn_utilities.gcp.datastore_manager import DataStoreManager
from cloud_fn_utilities.globals import DatastoreKeyTypes
from cloud_fn_utilities.state_managers.server_states import ServerStateManager

__author__ = "Philip Huff"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class FixedArenaStateManager:
    class States(Enum):
        START = 0
        BUILDING_ASSESSMENT = 1
        BUILDING_NETWORKS = 2
        COMPLETED_NETWORKS = 3
        BUILDING_SERVERS = 4
        COMPLETED_SERVERS = 5
        BUILDING_FIREWALL = 6
        COMPLETED_FIREWALL = 7
        BUILDING_ROUTES = 8
        COMPLETED_ROUTES = 9
        BUILDING_FIREWALL_RULES = 10
        COMPLETED_FIREWALL_RULES = 11
        BUILDING_STUDENT_ENTRY = 12
        COMPLETED_STUDENT_ENTRY = 13
        GUACAMOLE_SERVER_LOAD_TIMEOUT = 28
        RUNNING = 50
        STOPPING = 51
        STARTING = 52
        READY = 53
        EXPIRED = 60
        MISFIT = 61
        BROKEN = 62
        DELETING_SERVERS = 70
        COMPLETED_DELETING_SERVERS = 71
        DELETED = 72

    COMPLETION_STATES = [States.COMPLETED_DELETING_SERVERS, States.COMPLETED_FIREWALL, States.COMPLETED_NETWORKS,
                         States.COMPLETED_ROUTES, States.COMPLETED_SERVERS, States.COMPLETED_STUDENT_ENTRY]

    def __init__(self, initial_build_id=None):
        self.s = FixedArenaStateManager.States
        self.server_states = ServerStateManager.States
        if initial_build_id:
            self.ds = DataStoreManager(key_type=DatastoreKeyTypes.FIXED_ARENA, key_id=initial_build_id)
            self.build = self.ds.get()
            if 'state' not in self.build:
                self.build['state'] = self.s.START.value
                self.build['state-timestamp'] = datetime.utcnow().isoformat()
        else:
            self.ds = None
            self.build = None

    def set_build_record(self, build_id):
        self.ds = DataStoreManager(key_type=DatastoreKeyTypes.FIXED_ARENA, key_id=build_id)
        self.build = self.ds.get()
        if 'state' not in self.build:
            self.build['state'] = self.s.START.value
            self.build['state-timestamp'] = datetime.utcnow().isoformat()

    def state_transition(self, new_state):
        """
        Consistently changes a datastore entity with the necessary state checks.
        :param entity: A datastore entity
        :param new_state: The new state for the server
        :return: Boolean on success. If the state transition is valid, then return True. Otherwise, return False
        """
        existing_state = self.build['state']
        if self._is_fixed_arena_valid_transition(existing_state, new_state):
            self.build['state'] = new_state.value
            self.build['state-timestamp'] = datetime.utcnow().isoformat()
            if new_state == self.States.DELETED:
                self.build['active'] = False
            elif new_state == self.States.READY:
                self.build['active'] = True
            logging.info(f"State Transition {self.build.key.name}: Transitioning from {self.s(existing_state).name} to "
                         f"{self.s(new_state).name}")
            self.ds.put(self.build)
            return True
        else:
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
                if server.get('state', None) != self.server_states.STOPPED:
                    servers_finished = False
            if not servers_finished:
                time.sleep(sleep_time)
                wait_time += sleep_time
        if servers_finished:
            return True
        else:
            return False

    def _is_fixed_arena_valid_transition(self, existing_state, new_state):
        if new_state == self.s.START and not existing_state:
            return True
        elif new_state == self.s.BUILDING_NETWORKS and existing_state in \
                [self.s.START, self.s.BROKEN, self.s.BUILDING_NETWORKS]:
            return True
        elif new_state == self.s.BUILDING_SERVERS and existing_state in \
                [self.s.COMPLETED_NETWORKS, self.s.BUILDING_SERVERS]:
            return True
        elif new_state == self.s.BUILDING_ROUTES and existing_state in \
                [self.s.COMPLETED_SERVERS, self.s.BUILDING_ROUTES]:
            return True
        elif new_state == self.s.BUILDING_FIREWALL and \
                existing_state in [self.s.COMPLETED_ROUTES, self.s.COMPLETED_SERVERS, self.s.COMPLETED_NETWORKS,
                                   self.s.BUILDING_FIREWALL]:
            return True
        elif new_state == self.s.READY and existing_state in [self.s.COMPLETED_SERVERS]:
            return True
        elif new_state in self.COMPLETION_STATES:
            return True
        else:
            logging.warning(f"Invalid build state transition! Attempting to move to {self.s(new_state).name}, but "
                            f"the build is currently in the state {self.s(existing_state).name}")
            return False
