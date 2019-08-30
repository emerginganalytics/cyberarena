import argparse
import os
import time
import googleapiclient.discovery
import calendar
from six.moves import input
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta, date
from google.cloud import datastore

ds_client = datastore.Client()
compute = googleapiclient.discovery.build('compute', 'v1')

def isReadyToDelete(created_date):
    now = datetime.now()
    print(now)
    intance_creation_date = datetime.strptime(created_date[:19], '%Y-%m-%dT%H:%M:%S')
    print(intance_creation_date)
    delta = now - intance_creation_date
    print (delta.days)


# retrieve all workout rows information
list_info_workout = []
list_workout_id = []
def retrieve_workout_info():
    query_user = ds_client.query(kind='cybergym-workout')
    for workout in list(query_user.fetch()):
        list_info_workout.append(workout)
        list_workout_id.append(workout['workout_ID'])


# store the vm name into a list
list_vm_workout = []

def retrieve_all_vm(compute, project, zone):

    result = compute.instances().list(project=project, zone=zone).execute()

    try:
        for vm_instance in result['items']:
            list_vm_workout.append(vm_instance)
    except():
        print("No VM found")

    # test only the instances created for t workout --> contain "team" inside their names
    for instance in list_vm_workout:
        if "team" in instance['name']:
            isReadyToDelete(instance['creationTimestamp'])


# del_expired_instances(compute, 'ualr-cybersecurity', 'us-central1-a')

retrieve_workout_info()
retrieve_all_vm(compute, 'ualr-cybersecurity','us-central1-a')


print("\n")

for vm in list_vm_workout:
    for w_id in list_workout_id:
        if (w_id in vm["name"]):
            print(w_id) 




