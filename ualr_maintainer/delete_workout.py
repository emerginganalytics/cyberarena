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
def retrieve_workout_info():
    query_user = ds_client.query(kind='cybergym-workout')
    for workout in list(query_user.fetch()):
        list_info_workout.append(workout)



# delete all expired instances

def del_expired_instances(compute, project, zone):

    # store the vm name into a list
    list_vm_workout = []

    result = compute.instances().list(project=project, zone=zone).execute()

    try:
        for vm_instance in result['items']:
            list_vm_workout.append(vm_instance)
    except():
        print("No VM found")

    # test only the instances created for t workout --> contain "team" inside their names
    for instance in list_vm:
        if "team" in instance['name']:
            print(instance['name'])
            print("creation date of the vm :", instance['creationTimestamp'])
            isReadyToDelete(instance['creationTimestamp'])


# del_expired_instances(compute, 'ualr-cybersecurity', 'us-central1-a')

retrieve_workout_info()



for workout in list_info_workout:
    print(type(workout))
    print(workout['workout_ID']) 
    print(workout['user_email']) 
    print(workout['expiration']) 

    print(workout.id)

    if (int(workout['expiration'])) == 1:
        print("yo")

