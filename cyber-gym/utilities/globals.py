import sys
import logging
import googleapiclient.discovery
from google.cloud import datastore, storage, runtimeconfig
from google.cloud import logging as g_logging


runtimeconfig_client = runtimeconfig.Client()
myconfig = runtimeconfig_client.config('cybergym')
project = myconfig.get_variable('project').value.decode("utf-8")
region = myconfig.get_variable('region').value.decode("utf-8")
zone = myconfig.get_variable('zone').value.decode("utf-8")
dns_suffix = myconfig.get_variable('dns_suffix').value.decode("utf-8")
script_repository = myconfig.get_variable('script_repository').value.decode("utf-8")
api_key = myconfig.get_variable('api_key').value.decode("utf-8")

ds_client = datastore.Client()
compute = googleapiclient.discovery.build('compute', 'v1')
storage_client = storage.Client()
log_client = g_logging.Client()
dnszone = 'cybergym-public'
workout_token = 'RG987S1GVNKYRYHYA'

auth_config = {
    'api_key': api_key,
    'auth_domain': str(project + ".firebaseapp.com"),
    'project_id': project
}

# Use this for debugging. Uncomment the above endpoint for final environment.
post_endpoint = 'http://localhost:8080/complete'
logger = logging.getLogger()

class workout_globals():
    MAX_RUN_HOURS = 10
    yaml_bucket = project + '_cloudbuild'
    yaml_folder = 'yaml-build-files/'
    windows_startup_script_env = 'setx WORKOUTID {env_workoutid}\n'
    windows_startup_script_task = 'setx WORKOUTKEY_{q_number} {env_workoutkey}\n' \
                                  'call gsutil cp ' + script_repository + '{script} .\n' \
                                  'schtasks /Create /SC MINUTE /TN {script_name} /TR .\\{script}'
    max_workout_len = 30
    max_num_workouts = 30
    ps_build_workout_topic = 'build-workouts'
    ps_build_arena_topic = 'build_arena'

    @staticmethod
    def extended_wait(project, zone, operation_id):
        max_wait = 3
        i = 0
        complete = False
        while not complete and i <= max_wait:
            try:
                compute.zoneOperations().wait(project=project, zone=zone, operation=operation_id).execute()
                complete = True
            except:
                i += 1

        if not complete:
            logger.error("Timeout for operation %s" % operation_id)
            return False
        else:
            return True

    @staticmethod
    def refresh_api():
        compute = googleapiclient.discovery.build('compute', 'v1')
        return compute