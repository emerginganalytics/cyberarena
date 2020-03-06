#
# This function is intended to be run in Google Cloud Functions as the handler to the stop_workout pub/sub topic
#

import googleapiclient.discovery
from datetime import datetime, timedelta, date
from google.cloud import datastore
import time
import calendar

# Global variables for this function
ds_client = datastore.Client()
compute = googleapiclient.discovery.build('compute', 'v1', cache_discovery=False)
expired_workout = []
project = 'ualr-cybersecurity'
zone = 'us-central1-a'
region = 'us-central1'
dnszone = 'cybergym-public'


def stop_workouts(event, context):
    # Get the current time to compare with the start time to see if a workout needs to stop
    ts = calendar.timegm(time.gmtime())

    # Query all workouts which have not been deleted
    query_workouts = ds_client.query(kind='cybergym-workout')
    query_workouts.add_filter("running", "=", True)
    for workout in list(query_workouts.fetch()):
        if "start_time" in workout and "run_hours" in workout:
            workout_id = workout.key.name
            start_time = int(workout.get('start_time', 0))
            run_hours = int(workout.get('run_hours', 0))

            # Stop the workout servers if the run time has exceeded the request
            if ts - start_time >= run_hours * 3600:
                result = compute.instances().list(project=project, zone=zone,
                                                  filter='name = {}*'.format(workout_id)).execute()
                try:
                    if 'items' in result:
                        for vm_instance in result['items']:
                            response = compute.instances().stop(project=project, zone=zone,
                                                                instance=vm_instance["name"]).execute()
                    else:
                        print("No Virtual Machines to stop for workout %s" % workout_id)
                except KeyError:
                    print("Error when stopping in finding key in workout %s" % workout_id)
                    pass

        workout['running'] = False
        ds_client.put(workout)
        print('Stopped servers for workout %s' % workout_id)

stop_workouts(None, None)
