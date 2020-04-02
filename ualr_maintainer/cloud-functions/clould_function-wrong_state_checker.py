#
# This function is intended to be run in Google Cloud Functions as the handler to the wrong_state_checker
#

import googleapiclient.discovery
from google.cloud import datastore

# Global variables for this function
ds_client = datastore.Client()
compute = googleapiclient.discovery.build('compute', 'v1', cache_discovery=False)
expired_workout = []
project = 'ualr-cybersecurity'
zone = 'us-central1-a'
region = 'us-central1'
dnszone = 'cybergym-public'


def wrong_state_checker(event, context):
    # State change errors may occur in the application. In those cases, check to see if there are any non-expired
    # servers with a running state of false, but who have servers running. We want to stop these servers and fix
    # the stored state
    query_workouts = ds_client.query(kind='cybergym-workout')
    query_workouts.add_filter("resources_deleted", "=", False)
    query_workouts.add_filter("running", "=", False)
    for workout in list(query_workouts.fetch()):
        workout_id = workout.key.name
        if workout_id == 'fuiufa':
            a = 1
        result = compute.instances().list(project=project, zone=zone,
                                          filter='name = {}*'.format(workout_id)).execute()
        try:
            if 'items' in result:
                for vm_instance in result['items']:
                    response = compute.instances().get(project=project, zone=zone,
                                                        instance=vm_instance["name"]).execute()
                    if response["status"] != "TERMINATED":
                        compute.instances().stop(project=project, zone=zone,
                                                        instance=vm_instance["name"]).execute()
            else:
                print("No Virtual Machines to stop for workout %s" % workout_id)
        except KeyError:
            print("Error when stopping in finding key in workout %s" % workout_id)
            pass

wrong_state_checker(None, None)