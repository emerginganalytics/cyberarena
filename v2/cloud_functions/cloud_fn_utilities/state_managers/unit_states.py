import time
from datetime import datetime
from enum import Enum, EnumMeta

from cloud_fn_utilities.gcp.datastore_manager import DataStoreManager
from cloud_fn_utilities.globals import DatastoreKeyTypes, WorkoutStates, UnitStates
from cloud_fn_utilities.gcp.cloud_logger import Logger

__author__ = "Philip Huff"
__copyright__ = "Copyright 2023, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class UnitStateManager:
    MAX_WAIT_TIME = 500
    SLEEP_TIME = 10

    def __init__(self, build_id=None):
        self.s = UnitStates
        self.logger = Logger("cloud_functions.unit_states").logger
        self.workout_states = WorkoutStates
        if build_id:
            self.ds = DataStoreManager(key_type=DatastoreKeyTypes.UNIT, key_id=build_id)
            self.build = self.ds.get()
            if 'state' not in self.build:
                self.build['state'] = self.s.START.value
                self.build['state-timestamp'] = datetime.utcnow().isoformat()
                self.ds.put(self.build)
            self.build_id = build_id
        else:
            self.ds = None
            self.build = None
            self.build_id = None

    def set_build_record(self, build_id):
        self.ds = DataStoreManager(key_type=DatastoreKeyTypes.UNIT, key_id=build_id)
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
        self.ds.put(self.build)

    def get_state(self):
        return self.build['state']

    def get_state_timestamp(self):
        return self.build['state-timestamp']

    def are_workouts_deleted(self):
        return self._workout_state_check(workout_states=[self.workout_states.DELETED.value,
                                                         self.workout_states.BROKEN.value])


    def _workout_state_check(self, workout_states):
        wait_time = 0
        check_complete = False
        while not check_complete and wait_time < self.MAX_WAIT_TIME:
            check_complete = True
            workouts = self.ds.get_children(child_key_type=DatastoreKeyTypes.WORKOUT, parent_id=self.build_id)
            for workout in workouts:
                if workout.get('state', None) not in workout_states:
                    check_complete = False
                    continue
            if not check_complete:
                time.sleep(self.SLEEP_TIME)
                wait_time += self.SLEEP_TIME
        if check_complete:
            return True
        else:
            return False
