import sys
import googleapiclient.discovery
from google.cloud import datastore, storage

ds_client = datastore.Client()
compute = googleapiclient.discovery.build('compute', 'v1')
storage_client = storage.Client()
dns_suffix = ".cybergym-eac-ualr.org"
project = 'ualr-cybersecurity'
dnszone = 'cybergym-public'
workout_token = 'RG987S1GVNKYRYHYA'
region = 'us-central1'
zone = 'us-central1-a'
#post_endpoint = 'https://buildthewarrior.cybergym-eac-ualr.org/complete'

# Use this for debugging. Uncomment the above endpoint for final environment.
post_endpoint = 'http://localhost:8080/complete'

class workout_globals():
    MAX_RUN_HOURS = 10
    yaml_bucket = project + '_cloudbuild'
    yaml_folder = 'yaml-build-files/'

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
            print("Timeout for operation %s" % operation_id)
            return False
        else:
            return True

    @staticmethod
    def refresh_api():
        compute = googleapiclient.discovery.build('compute', 'v1')
        return compute