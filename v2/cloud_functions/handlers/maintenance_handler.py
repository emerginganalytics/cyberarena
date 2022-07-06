import logging
from calendar import calendar
from datetime import time
from google import pubsub_v1
from google.cloud import logging_v2
from cloud_fn_utilities.globals import PubSub, DatastoreKeyTypes, BuildConstants
from cloud_fn_utilities.gcp.cloud_env import CloudEnv
from cloud_fn_utilities.gcp.compute_manager import ComputeManager
from cloud_fn_utilities.gcp.pubsub_manager import PubSubManager


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
        # query_old_units = ds_client.query(kind = 'cybergym-unit')
        # query_old_units.add_filter("timestamp", ">", str(calendar.timegm(time.gmtime()) - self.DEFAULT_LOOKBACK))
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

    def start(self):
        """
        Starts a server based on the specification in the Datastore entity with name server_name. A guacamole server
        is also registered with DNS.
        """
        state_manager = ServerStateManager(initial_build_id=self.server_name)
        state_manager.state_transition(self.s.STARTING)
        i = 0
        start_success = False
        while not start_success and i < 5:
            try:
                if "delayed_start" in self.server_spec and self.server_spec["delayed_start"]:
                    time.sleep(30)
                response = self.compute.instances().start(project=self.env.project, zone=self.env.zone,
                                                          instance=self.server_name).execute()
                start_success = True
                logging.info(f'Sent job to start {self.server_name}, and waiting for response')
            except BrokenPipeError:
                i += 1
        i = 0
        success = False
        while not success and i < 5:
            try:
                self.compute.zoneOperations().wait(project=self.env.project, zone=self.env.zone,
                                                   operation=response["id"]).execute()
                success = True
            except timeout:
                i += 1
                logging.warning(f'Response timeout for starting server {self.server_name}. Trying again')
                pass
        if not success:
            logging.error(f'Timeout in trying to start server {self.server_name}')
            state_manager.state_transition(self.s.BROKEN)
            raise ConnectionError

        # If the server is an external proxy, then register its DNS name
        dns_hostname = self.server_spec.get('dns_hostname', None)
        if dns_hostname:
            dns_record = dns_hostname + self.env.dns_suffix + "."
            self.dns_manager.add_dns_record(dns_record, self.server_name)

        state_manager.state_transition(self.s.RUNNING)
        logging.info(f"Finished starting {self.server_name}")

    def nuke(self):
        """
        Deletes a server based on the specification in the Datastore entity with the name server_name. Then rebuilds
        the server.
        """
        self.delete()
        self.build()