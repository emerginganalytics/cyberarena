import googleapiclient.discovery
from datetime import datetime, timedelta, date
from google.cloud import datastore
import time
import calendar

# Global variables for this function
compute = googleapiclient.discovery.build('compute', 'v1', cache_discovery=False)
project = 'ualr-cybersecurity'
zone = 'us-central1-a'
region = 'us-central1'
dnszone = 'cybergym-public'


def stop_workout(workout_id):
    result = compute.instances().list(project=project, zone=zone,
                                      filter='name = {}*'.format(workout_id)).execute()
    for vm_instance in result['items']:
        response = compute.instances().stop(project=project, zone=zone,
                                            instance=vm_instance["name"]).execute()
