import sys
import logging
import googleapiclient.discovery
from google.cloud import datastore, storage

ds_client = datastore.Client()
compute = googleapiclient.discovery.build('compute', 'v1')
storage_client = storage.Client()
region = 'us-central1'
# dns_suffix = ".acactb.com"
# project = 'acapte'
# dnszone = 'aca-bootcamp-public'
dns_suffix = ".cybergym-eac-ualr.org"
project = 'ualr-cybersecurity'
dnszone = 'cybergym-public'
workout_token = 'RG987S1GVNKYRYHYA'
script_repository = 'gs://ualr-cybersecurity_cloudbuild/startup-scripts/'
#post_endpoint = 'https://buildthewarrior.cybergym-eac-ualr.org/complete'

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