#
# This function is intended to be run in Google Cloud Functions as the handler to the maintenance pub/sub topic
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


# IN PROGRESS
# to be update with expiration date query from datastore
def workout_age(created_date):
    now = datetime.now()
    instance_creation_date = datetime.fromtimestamp(int(created_date))
    delta = now - instance_creation_date
    return delta.days


def delete_vms(workout_id):
    result = compute.instances().list(project=project, zone=zone, filter='name = {}*'.format(workout_id)).execute()
    try:
        if 'items' in result:
            for vm_instance in result['items']:
                response = compute.instances().delete(project=project, zone=zone,
                                           instance=vm_instance["name"]).execute()
            compute.zoneOperations().wait(project=project, zone=zone, operation=response["id"]).execute()
        else:
            print("No Virtual Machines to delete for workout %s" % workout_id)
        return True
    except():
        print("Error in deleting VM for %s" % workout_id)
        return False


def delete_firewall_rules(workout_id):
    try:
        result = compute.firewalls().list(project=project, filter='name = {}*'.format(workout_id)).execute()
        if 'items' in result:
            for fw_rule in result['items']:
                response = compute.firewalls().delete(project=project, firewall=fw_rule["name"]).execute()
            compute.zoneOperations().wait(project=project, zone=zone, operation=response["id"]).execute()
        return True
    except():
        print("Error in deleting firewall rules for %s" % workout_id)
        return False


def delete_subnetworks(workout_id):
    try:
        result = compute.subnetworks().list(project=project, region=region,
                                              filter='name = {}*'.format(workout_id)).execute()
        if 'items' in result:
            for subnetwork in result['items']:
                response = compute.subnetworks().delete(project=project, region=region,
                                                       subnetwork=subnetwork["name"]).execute()
            compute.zoneOperations().wait(project=project, zone=zone, operation=response["id"]).execute()
        return True
    except():
        print("Error in deleting subnetworks for %s" % workout_id)
        return True


def delete_network(workout_id):
    try:
        result = compute.networks().list(project=project, filter='name = {}*'.format(workout_id)).execute()
        if 'items' in result:
            for network in result['items']:
                compute.networks().delete(project=project, network=network["name"]).execute()
        return True
    except():
        print("Error in deleting network for %s" % workout_id)
        return False


def delete_workouts(event, context):
    query_workouts = ds_client.query(kind='cybergym-workout')
    # Only process the workouts from the last month. 2628000 is the number of seconds in a month
    query_workouts.add_filter("timestamp", ">", str(calendar.timegm(time.gmtime()) - 2628000))
    for workout in list(query_workouts.fetch()):
        if 'resources_deleted' not in workout:
            workout['resources_deleted'] = False
        if workout_age(workout['timestamp']) >= int(workout['expiration']) and not workout['resources_deleted']:
            print('Deleting resources from workout %s', workout['workout_ID'])
            expired_id = workout['workout_ID']
            if delete_vms(expired_id):
                if delete_firewall_rules(expired_id):
                    if delete_subnetworks(expired_id):
                        if delete_network(expired_id):
                            workout['resources_deleted'] = True
                            ds_client.put(workout)


# The main function is only for debugging. Do not include this line in the cloud function
delete_workouts(None, None)