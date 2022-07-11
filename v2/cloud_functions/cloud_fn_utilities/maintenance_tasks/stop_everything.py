import googleapiclient
import schedule
from google.cloud import logging_v2
from self import self

from cloud_fn_utilities.gcp.cloud_env import CloudEnv
from common.globals import compute, LOG_LEVELS, project, zone
from main import log_client


class StopEverything(self):
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
        #self.s = ServerStateManag.States
        #self.server_spec = DataStoreManager(key_type=DatastoreKeyTypes.SERVER, key_id=self.event_attributes).get()
        self.compute = googleapiclient.discovery.build('compute', 'v1')
        #self.server_states = ServerStateManag.States
        # self.lookback_seconds = self.lookback_seconds

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

     schedule.every().day.at("00:00").do(stop_server, self)