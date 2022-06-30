import time
from datetime import datetime
import calendar
from enum import Enum
import logging

from cloud_fn_utilities.gcp.datastore_manager import DataStoreManager
from cloud_fn_utilities.globals import DatastoreKeyTypes

__author__ = "Philip Huff"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class ServerStateManager:

    class States(Enum):
        START = 0
        BUILDING = 1
        READY = 2
        STARTING = 3
        RUNNING = 4
        STOPPING = 5
        STOPPED = 6
        EXPIRED = 7
        MISFIT = 8
        RESETTING = 9
        RELOADING = 10
        BROKEN = 11
        DELETING = 12
        DELETED = 13

    def __init__(self, initial_build_id=None):
        self.s = ServerStateManager.States
        if initial_build_id:
            self.ds = DataStoreManager(key_type=DatastoreKeyTypes.SERVER, key_id=initial_build_id)
            self.build = self.ds.get()
            if 'state' not in self.build:
                self.build['state'] = self.s.START.value
                self.build['state-timestamp'] = datetime.utcnow().isoformat()
        else:
            self.ds = None
            self.build = None

    def set_build_record(self, build_id):
        self.ds = DataStoreManager(key_type=DatastoreKeyTypes.SERVER, key_id=build_id)
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
        self.build['state'] = new_state.value
        self.build['state-timestamp'] = datetime.utcnow().isoformat()
        logging.info(f"State Transition {self.build.key.name}: Transitioning from "
                     f"{self.s(existing_state).name} to {self.s(new_state).name}")
        self.ds.put(self.build)
        return True

    def get_state(self):
        return self.build['state']

    def get_state_timestamp(self):
        return self.build['state-timestamp']
