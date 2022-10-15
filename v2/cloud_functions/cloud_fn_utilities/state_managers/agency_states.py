import time
from datetime import datetime
from enum import Enum
import logging
from cloud_fn_utilities.gcp.datastore_manager import DataStoreManager
from cloud_fn_utilities.globals import DatastoreKeyTypes, ServerStates

__author__ = "Andrew Bomberger"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Andrew Bomberger"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class AgencyStateManager:
    class States(Enum):
        START = 0
        BUILDING_PUBSUB = 1
        COMPLETED_PUBSUB = 2
        CHECKING_AGENT = 3
        MISSING_AGENT = 4
        BUILDING_AGENT = 5
        COMPLETED_AGENT = 6
        BUILDING_INJECT = 7
        COMPLETED_BUILDING_INJECT = 8
        TESTING_CLIENT = 9
        FAILED_TESTING_CLIENT = 10
        COMPLETED_TESTING_CLIENT = 11
        READY = 52
        MISFIT = 61
        BROKEN = 62
        DELETING_AGENT = 68
        COMPLETED_DELETING_AGENT = 69
        DELETING_AGENT_TOPIC = 70
        COMPLETED_DELETING_AGENT_TOPIC = 71
        DELETED = 72

    COMPLETION_STATES = [States.COMPLETED_AGENT, States.COMPLETED_PUBSUB, States.COMPLETED_DELETING_AGENT_TOPIC,
                         States.COMPLETED_DELETING_AGENT, States.COMPLETED_TESTING_CLIENT,
                         States.COMPLETED_BUILDING_INJECT]

    def __init__(self, initial_build_id=None):
        self.s = AgencyStateManager.States
        self.server_states = ServerStates
        if initial_build_id:
            self.ds = DataStoreManager(key_type=DatastoreKeyTypes.FIXED_ARENA, key_id=initial_build_id)
            self.build = self.ds.get()
            if 'state' not in self.build:
                self.build['state'] = self.s.START.value
                self.build['state-timestamp'] = datetime.utcnow().isoformat()
        else:
            self.ds = None
            self.build = None

    # TODO: Need to update methods to match Agency build state process
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
        if self._is_agency_valid_transition(existing_state, new_state):
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

    def _is_agency_valid_transition(self, existing_state, new_state):
        # TODO: Rework fixed_arena_states logic to match the Agency state model
        logging.warning(f"Invalid build state transition! Attempting to move to {self.s(new_state).name}, but "
                        f"the build is currently in the state {self.s(existing_state).name}")
        return False
