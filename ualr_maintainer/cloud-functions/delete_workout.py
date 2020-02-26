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
project = 'apacte'
zone = 'us-central1-a'
region = 'us-central1'
dnszone = 'cybergym-public'


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
            time.sleep(60)
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
            compute.globalOperations().wait(project=project, operation=response["id"]).execute()
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
            compute.regionOperations().wait(project=project, region=region, operation=response["id"]).execute()
        return True
    except():
        print("Error in deleting subnetworks for %s" % workout_id)
        return True


def delete_network(workout_id):
    try:
        # First delete any routes specific to the workout
        result = compute.routes().list(project=project, filter='name = {}*'.format(workout_id)).execute()
        if 'items' in result:
            for route in result['items']:
                response = compute.routes().delete(project=project, route=route["name"]).execute()
            compute.globalOperations().wait(project=project, operation=response["id"]).execute()

        # Now it is safe to delete the networks.
        result = compute.networks().list(project=project, filter='name = {}*'.format(workout_id)).execute()
        if 'items' in result:
            for network in result['items']:
                compute.networks().delete(project=project, network=network["name"]).execute()
        return True
    except():
        print("Error in deleting network for %s" % workout_id)
        return False

def delete_dns(workout_id, ip_address):
    try:
        service = googleapiclient.discovery.build('dns', 'v1')

        change_body = {"deletions": [
            {
                "kind": "dns#resourceRecordSet",
                "name": workout_id + ".cybergym-eac-ualr.org.",
                "rrdatas": [ip_address],
                "type": "A",
                "ttl": 30
            }
        ]}

        request = service.changes().create(project=project, managedZone=dnszone, body=change_body)
        response = request.execute()
    except():
        print("Error in deleting DNS record for workout %s" % workout_id)
        return False
    return True


def delete_workouts(event, context):
    query_workouts = ds_client.query(kind='cybergym-workout')
    # Only process the workouts from the last month. 2628000 is the number of seconds in a month
    query_workouts.add_filter("timestamp", ">", str(calendar.timegm(time.gmtime()) - 2628000))
    for workout in list(query_workouts.fetch()):
        if 'resources_deleted' not in workout:
            workout['resources_deleted'] = False
        if workout['resources_deleted']:
            print('Deleting resources from workout %s' % workout['workout_ID'])
            expired_id = workout.key

            # First, delete the DNS entries associated with this workout.
            if "external_ip" in workout:
                delete_dns(expired_id, workout["external_ip"])
            if delete_vms(expired_id):
                if delete_firewall_rules(expired_id):
                    if delete_subnetworks(expired_id):
                        if delete_network(expired_id):
                            workout['resources_deleted'] = True
                            ds_client.put(workout)


# This function is only for local testing
def delete_specific_workout(workout_ID):
    query_workouts = ds_client.query(kind='cybergym-workout')
    first_key = ds_client.key('cybergym-workout', workout_ID)
    query_workouts.key_filter(first_key, '=')
    for workout in list(query_workouts.fetch()):
        if 'resources_deleted' not in workout:
            workout['resources_deleted'] = False
        if not workout['resources_deleted']:
            print('Deleting resources from workout %s' % workout_ID)
            if "external_ip" in workout:
                delete_dns(workout_ID, workout["external_ip"])
            if delete_vms(workout_ID):
                if delete_firewall_rules(workout_ID):
                    if delete_subnetworks(workout_ID):
                        if delete_network(workout_ID):
                            workout['resources_deleted'] = True
                            ds_client.put(workout)

# The main function is only for debugging. Do not include this line in the cloud function
# delete_workouts(None, None)

delete_workouts = ['sukulr']
for workout in delete_workouts:
    delete_specific_workout(workout)
