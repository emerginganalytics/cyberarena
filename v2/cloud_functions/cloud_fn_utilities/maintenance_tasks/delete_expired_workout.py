from calendar import calendar
from datetime import time

import schedule
from google import pubsub_v1
from self import self

from cloud_fn_utilities.gcp.datastore_manager import DataStoreManager
from cloud_fn_utilities.globals import DatastoreKeyTypes
from common.globals import WORKOUT_TYPES, ArenaWorkoutDeleteType, ds_client, BUILD_STATES, PUBSUB_TOPICS, project, \
    LOG_LEVELS, cloud_log
from common.state_transition import state_transition

DEFAULT_LOOKBACK = 10512000

class DeleteExpiredWorkout:

    class DeleteType:
     EXPIRED = "Expired"

    def __init__(self, deletion_type=DeleteType.EXPIRED, build_id=None, build_type=WORKOUT_TYPES.WORKOUT,
                 lookback_seconds=DEFAULT_LOOKBACK):
        self.deletion_type = deletion_type
        self.build_id = build_id
        self.build_type = build_type
        self.lookback_seconds = lookback_seconds

    def run(self, deletion_type=None):

        if deletion_type:
            self.deletion_type = deletion_type

        if self.deletion_type == self.DeletionType.EXPIRED:
            if self.build_type == WORKOUT_TYPES.WORKOUT:
                self._delete_expired_workouts()
            elif self.build_type == WORKOUT_TYPES.ARENA:
                self._delete_expired_arenas()

        return True

    def __init__(self):
        self.df = DataStoreManager(key_type=DatastoreKeyTypes.FIXED_ARENA_WORKOUT)

    def _delete_expired_arenas(self):

        query_old_units = ds_client.query(kind='cybergym-unit')
        query_old_units.add_filter("timestamp", ">", str(calendar.timegm(time.gmtime()) - self.lookback_seconds))
        for unit in list(query_old_units.fetch()):
            arena_type = False
            if 'build_type' in unit and unit['build_type'] == 'arena':
                arena_type = True

            if arena_type:
                try:
                    unit_state = unit.get('state', None)
                    unit_deleted = True if not unit_state or unit_state == BUILD_STATES.DELETED else False
                    if self._workout_age(unit['timestamp']) >= int(unit['expiration']) \
                            and not unit_deleted:
                        state_transition(unit, BUILD_STATES.READY_DELETE)
                        pubsub_topic = PUBSUB_TOPICS.DELETE_EXPIRED
                        publisher = pubsub_v1.PublisherClient()
                        topic_path = publisher.topic_path(project, pubsub_topic)
                        publisher.publish(topic_path, data=b'Workout Delete', workout_type=WORKOUT_TYPES.ARENA,
                                          unit_id=unit.key.name)
                except KeyError:
                    state_transition(unit, BUILD_STATES.DELETED)
        cloud_log("delete_arenas", f"Deleted expired arenas", LOG_LEVELS.INFO)

    schedule.every(1).hours.do(_delete_expired_arenas,self)