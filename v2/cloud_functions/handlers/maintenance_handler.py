import logging
from calendar import calendar
from datetime import time, datetime

import googleapiclient
from google import pubsub_v1
from google.cloud import logging_v2
from googleapiclient.errors import HttpError
from joblib import disk
from joblib.testing import timeout

from cloud_fn_utilities.gcp.datastore_manager import DataStoreManager
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

from cloud_fn_utilities.server_specific.fixed_arena_workspace_proxy import FixedArenaWorkspaceProxy
from cloud_fn_utilities.state_managers.fixed_arena_states import FixedArenaStateManager

from cloud_fn_utilities.state_managers.server_states import ServerStateManag

from common.globals import log_client, compute, project, zone, LOG_LEVELS, ds_client, BUILD_STATES, PUBSUB_TOPICS, \
    WORKOUT_TYPES, cloud_log, workout_globals, SERVER_STATES, SERVER_ACTIONS, dns_suffix, parent_project, dnszone, \
    gcp_operation_wait
from common.state_transition import state_transition



class MaintenanceHandler:
    def __init__(self, event_attributes):
        self.state_manager = None
        self.server_name = event_attributes
        self.fixed_arena_workspace_ids = None
        self.env = CloudEnv()
        self.DEFAULT_LOOKBACK = 10512000
#        self.lookback_seconds = self.lookback_seconds
        log_client = logging_v2.Client()
        log_client.setup_logging()
        self.event_attributes = event_attributes
        self.s = ServerStateManag.States
        self.server_spec = DataStoreManager(key_type=DatastoreKeyTypes.SERVER, key_id=self.event_attributes).get()
        self.compute = googleapiclient.discovery.build('compute', 'v1')
        self.server_states = ServerStateManag.States
        #self.lookback_seconds = self.lookback_seconds

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

    def _delete_expired_workouts(self):

        query_old_workouts = ds_client.query(kind='cybergym-workout')
        query_old_workouts.add_filter('active', '=', True)

        for workout in list(query_old_workouts.fetch()):
            workout_project = workout.get('build_project_location', project)
            if workout_project == project:
                if 'state' not in workout:
                    workout['state'] = BUILD_STATES.DELETED
                container_type = False
                # If the workout is a container, then expire the container so it does not show up in the list of running workouts.
                if 'build_type' in workout and workout['build_type'] == 'container':
                    container_type = True
                    if 'timestamp' not in workout or 'expiration' not in workout and \
                            workout['state'] != BUILD_STATES.DELETED:
                        state_transition(workout, BUILD_STATES.DELETED)
                    elif self._workout_age(workout['timestamp']) >= int(workout['expiration']) and \
                            workout['state'] != BUILD_STATES.DELETED:
                        state_transition(workout, BUILD_STATES.DELETED)

                arena_type = False
                if 'build_type' in workout and workout['build_type'] == 'arena' or \
                        'type' in workout and workout['type'] == 'arena':
                    arena_type = True

                if not container_type and not arena_type:
                    if self._workout_age(workout['timestamp']) >= int(workout['expiration']):
                        if workout['state'] != BUILD_STATES.DELETED:
                            state_transition(workout, BUILD_STATES.READY_DELETE)
                            workout_id = workout.key.name
                            # Delete the workouts asynchronously
                            pubsub_topic = PUBSUB_TOPICS.DELETE_EXPIRED
                            publisher = pubsub_v1.PublisherClient()
                            topic_path = publisher.topic_path(project, pubsub_topic)
                            publisher.publish(topic_path, data=b'Workout Delete', workout_type=WORKOUT_TYPES.WORKOUT,
                                              workout_id=workout_id)

    def _workout_age(self, created_date):
        now = datetime.now()
        instance_creation_date = datetime.fromtimestamp(int(created_date))
        delta = now - instance_creation_date
        return delta.days

    def delete_server(self, build_id):
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

    def create_snapshot(self,  max_snapshots=3, server_name=None):

        service = googleapiclient.discovery.build('compute', 'v1')


        found_available = False
        latest = 0
        latest_ts = '2000-01-01T00:00:00.000'
        i = 0


        while i < int(max_snapshots):
            try:
                response = service.snapshots().get(project=project, snapshot=server_name + str(i)).execute()
                if response['creationTimestamp'] > latest_ts:
                    latest_ts = response['creationTimestamp']
                    latest = i
                i += 1
            except HttpError:
                latest = (i - 1) % max_snapshots
                found_available = True
                break

        selected_snapshot = f"{server_name}{(latest + 1) % max_snapshots}"
        if not found_available:
            response = service.snapshots().delete(project=project, snapshot=selected_snapshot).execute()

            if not gcp_operation_wait(service=service, response=response, wait_type="global"):
                raise Exception(f"Timeout waiting for snapshot {selected_snapshot} to delete.")

        snapshot_body = {
            'name': selected_snapshot,
            'description': 'Production snapshot used for imaging'
        }

        response = service.disks().createSnapshot(project=project, zone=zone, disk=server_name, body=snapshot_body).execute()

        if not gcp_operation_wait(service=service, response=response):
            raise Exception(f"Timeout waiting for snapshot {selected_snapshot} to be created")

        return selected_snapshot

