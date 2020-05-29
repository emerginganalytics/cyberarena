#
# This function is intended to be run in Google Cloud Functions as the handler to the maintenance pub/sub topic
#

import googleapiclient.discovery
from datetime import datetime, timedelta, date
from google.cloud import datastore
import time
import calendar
from googleapiclient.errors import HttpError
import googleapiclient.discovery
from google.cloud import datastore

ds_client = datastore.Client()
compute = googleapiclient.discovery.build('compute', 'v1')
dns_suffix = ".cybergym-eac-ualr.org"
project = 'ualr-cybersecurity'
dnszone = 'cybergym-public'

# Global variables for this function
expired_workout = []
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
            time.sleep(60)
            try:
                compute.zoneOperations().wait(project=project, zone=zone, operation=response["id"]).execute()
            except:
                pass
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
            try:
                compute.zoneOperations().wait(project=project, zone=zone, operation=response["id"]).execute()
            except:
                pass
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
            try:
                compute.zoneOperations().wait(project=project, zone=zone, operation=response["id"]).execute()
            except:
                pass
        return True
    except():
        print("Error in deleting subnetworks for %s" % workout_id)
        return True


def long_delete_network(network, response):
    max_tries = 3
    i = 0
    while 'error' in response and i < max_tries:
        response = compute.networks().delete(project=project, network=network).execute()
        compute.globalOperations().wait(project=project, operation=response["id"]).execute()
        response = compute.globalOperations().get(project=project, operation=response["id"]).execute()
        i += 1

    if i < max_tries:
        return True
    else:
        return False

def delete_network(workout_id):
    try:
        # First delete any routes specific to the workout
        result = compute.routes().list(project=project, filter='name = {}*'.format(workout_id)).execute()
        if 'items' in result:
            for route in result['items']:
                response = compute.routes().delete(project=project, route=route["name"]).execute()
            try:
                compute.zoneOperations().wait(project=project, zone=zone, operation=response["id"]).execute()
            except:
                pass

        # Now it is safe to delete the networks.
        result = compute.networks().list(project=project, filter='name = {}*'.format(workout_id)).execute()
        if 'items' in result:
            for network in result['items']:
                # Networks are not being deleted because the operation occurs too fast.
                response = compute.networks().delete(project=project, network=network["name"]).execute()
                compute.globalOperations().wait(project=project, operation=response["id"]).execute()
                response = compute.globalOperations().get(project=project, operation=response["id"]).execute()
                if 'error' in response:
                     if not long_delete_network(network["name"], response):
                         return False
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
                "name": workout_id + dns_suffix + ".",
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


def delete_specific_workout(workout_id, workout):
        try:
            delete_dns(workout_id, workout["external_ip"])
        except HttpError:
            print("DNS record does not exist")
            pass
        except KeyError:
            print("workout %s has no external IP address" % workout_id)
            pass
        if delete_vms(workout_id):
            if delete_firewall_rules(workout_id):
                if delete_subnetworks(workout_id):
                    if delete_network(workout_id):
                        return True

        return False


def delete_temporary_workouts(duration_hours):
    # Only process the workouts from the last 4 months. 10512000 is the number of seconds in a month
    query_old_workouts = ds_client.query(kind='cybergym-workout')
    query_old_workouts.add_filter("timestamp", ">", str(calendar.timegm(time.gmtime()) - duration_hours*3600))
    for workout in list(query_old_workouts.fetch()):
        if 'resources_deleted' not in workout:
            workout['resources_deleted'] = False
        if workout_age(workout['timestamp']) >= int(workout['expiration']) and not workout['resources_deleted']:
            workout_id = None
            if workout.key.name:
                workout_id = workout.key.name
            elif "workout_ID" in workout:
                workout_id = workout["workout_ID"]

            if workout_id:
                print('Deleting resources from workout %s' % workout_id)
                if delete_specific_workout(workout_id, workout):
                    workout['resources_deleted'] = True
                    ds_client.put(workout)


def set_expiration(endtime, duration, user_email):
    starttime = endtime - duration*3600

    query_workouts = ds_client.query(kind='cybergym-workout')
    query_workouts.add_filter("timestamp", ">", str(starttime))
    query_workouts.add_filter("timestamp", "<", str(endtime))
    for workout in list(query_workouts.fetch()):
        if workout['user_email'] == user_email:
            workout['expiration'] = 0
            ds_client.put(workout)


duration_hours = 1
set_expiration(endtime=1590617890, duration=duration_hours, user_email='pdhuff@ualr.edu')
delete_temporary_workouts(duration_hours=duration_hours)
