import logging
from calendar import calendar
from datetime import time

from google import pubsub_v1
from google.cloud import logging_v2

from cloud_fn_utilities.globals import PubSub, DatastoreKeyTypes, BuildConstants
from cloud_fn_utilities.gcp.cloud_env import CloudEnv
from cloud_fn_utilities.gcp.compute_manager import ComputeManager

__author__ = "Philip Huff"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"

from common.globals import log_client, compute, project, zone, LOG_LEVELS, ds_client, BUILD_STATES, PUBSUB_TOPICS, \
    WORKOUT_TYPES, cloud_log, workout_globals, SERVER_STATES
from common.state_transition import state_transition



class MaintenanceHandler:
    def __init__(self, event_attributes):
        self.env = CloudEnv()
        self.DEFAULT_LOOKBACK = 10512000
        log_client = logging_v2.Client()
        log_client.setup_logging()
        self.event_attributes = event_attributes

    def route(self):
        action = self.event_attributes('action', None)
        if not action:
            logging.error(f"No action provided in cloud function maintenance handler")
            raise ValueError
        if action == PubSub.MaintenanceActions.START_SERVER:
            build_id = self.event_attributes.get('build_id', None)
            if not build_id:
                logging.error(f"No build id provided for maintenance handler with action {action}")
                raise ValueError
            ComputeManager(server_name=build_id).start()
        else:
            logging.error(f"Unsupported action supplied to the maintenance handler")
            raise ValueError

    def delete_server(self, build_id) -> object:
        #query_old_units = ds_client.query(kind = 'cybergym-unit')
        #query_old_units.add_filter("timestamp", ">", str(calendar.timegm(time.gmtime()) - self.DEFAULT_LOOKBACK))
        query_old_units = ds_client.query(kind='cybergym-workout')
        query_old_units.add_filter('workout_ID', '=', build_id)
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
                        publisher.publish(topic_path)
                except KeyError:
                    state_transition(unit, BUILD_STATES.DELETED)
        cloud_log("delete_arenas", f"Deleted expired arenas", LOG_LEVELS.INFO)

    def stop_server(self):
        g_logger = log_client.logger("workout-actions")
        result: object = compute.instances().list(project=project, zone=zone).execute()
        if 'items' not in result:
            g_logger.log_struct(
                {
                    "message": "No workouts to stop (daily cleanup)"
                }, severity=LOG_LEVELS.WARNING
                )
        else:
            for vm_instance in result['items']:
                response = compute.instances().stop(project=project, zone=zone,
                                                instance=vm_instance["name"]).execute()
        g_logger.log_struct(
            {
                "message": "All machines stopped (daily cleanup)",
            }, severity=LOG_LEVELS.INFO
        )

