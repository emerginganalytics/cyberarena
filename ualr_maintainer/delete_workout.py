#
# This function is intended to be run in Google Cloud Functions as the handler to the maintenance pub/sub topic
# Need to rewrite to delete based on expired workout and not loop through all resources each time.
#

import googleapiclient.discovery
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
    print(delta.days)


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


def retrieve_all_network(compute, project):
    try:
        result = compute.networks().list(project=project).execute()
        for network in result['items']:
            list_network.append(network)
    except():
        print("No Network found")


# store the different network
list_subnetwork = []
def retrieve_all_subnetwork(compute, project, region):
    try:
        response = compute.subnetworks().list(project=project, region=region).execute()
        for subnetwork in response['items']:
            list_subnetwork.append(subnetwork)
    except():
        print("No subnetworks found")


# store the different network
list_firewall_rules = []
def retrieve_all_firewall_rules(compute, project):
    try:
        response = compute.firewalls().list(project=project).execute()
        for fw_rule in response['items']:
            list_firewall_rules.append(fw_rule)
    except():
        print("No firewall rules found")


project = 'ualr-cybersecurity'
zone = 'us-central1-a'
region = 'us-central1'

# retrieve vm and query from datastore
retrieve_workout_info()
retrieve_all_vm(compute, project, zone)
retrieve_all_network(compute, project)
retrieve_all_subnetwork(compute, project, region)
retrieve_all_firewall_rules(compute, project)

# delete matching vm
for vm in list_vm_workout:
    for w_id in list_workout_id:
        if w_id in vm["name"]:
            print("Delete VM : ", vm["name"])
            request = compute.instances().delete(project=project, zone=zone,
                                                 instance=vm["name"])
            response = request.execute()

# delete matching firewall-rules
for fw_rule in list_vm_workout:
    for w_id in list_workout_id:
        if (w_id in fw_rule["name"]):
            print("Delete Firewall Rule : ", fw_rule["name"])
            request = compute.firewalls().delete(project=project, instance=fw_rule["name"])
            response = request.execute()

# delete matching subnetworks
for subnetwork in list_subnetwork:
    for w_id in list_workout_id:
        if (w_id in subnetwork["name"]):
            print("Delete network : ", subnetwork["name"])
            request = compute.subnetworks().delete(project=project, region=region, subnetwork=subnetwork["name"])
            response = request.execute()

# delete matching networks
for network in list_network:
    for w_id in list_workout_id:
        if (w_id in network["name"]):
            print("Delete network : ", network["name"])
            request = compute.networks().delete(project=project, network=network["name"])
            response = request.execute()
