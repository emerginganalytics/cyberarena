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

# IN PROGRESS
# to be update with expiration date query from datastore
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


# store the vm into a list
list_vm_workout = []
def retrieve_all_vm(compute, project, zone):
    result = compute.instances().list(project=project, zone=zone).execute()
    try:
        for vm_instance in result['items']:
            list_vm_workout.append(vm_instance)
    except():
        print("No VM found")


# store the different network
list_network = []
def retrieve_all_network(project="ualr-cybersecurity"):
    request = compute.networks().list(project=project)
    response = request.execute()
    for network in response['items']:
        list_network.append(network)





def delete_vm_network():
    # retrieve vm and query from datastore
    retrieve_workout_info()
    retrieve_all_vm(compute, 'ualr-cybersecurity','us-central1-a')
    retrieve_all_network()

    # delete matching vm
    for vm in list_vm_workout:
        for w_id in list_workout_id:
            if (w_id in vm["name"]):
                print("Delete VM : ", vm["name"]) 
                request = compute.instances().delete(project='ualr-cybersecurity', zone='us-central1-a', instance=vm["name"])
                response = request.execute()


# we also need to delete the created network
"""
for network in list_network:
    for w_id in list_workout_id:
        if (w_id in network["name"]):
            print("Delete network : ", network["name"])
            request = compute.networks().delete(project="ualr-cybersecurity", network=network["name"])
            response = request.execute()
"""




