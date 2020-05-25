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



def delete_workouts(event, context):
    # Only process the workouts from the last 4 months. 10512000 is the number of seconds in a month
    query_old_workouts = ds_client.query(kind='cybergym-workout')
    query_old_workouts.add_filter("timestamp", ">", str(calendar.timegm(time.gmtime()) - 10512000))
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

    query_misfit_workouts = ds_client.query(kind='cybergym-workout')
    query_misfit_workouts.add_filter("misfit", "=", True)
    for workout in list(query_misfit_workouts.fetch()):
        workout_id = None
        if workout.key.name:
            workout_id = workout.key.name
        elif "workout_ID" in workout:
            workout_id = workout["workout_ID"]

        if workout_id:
            print('Deleting resources from workout %s' % workout_id)
            if delete_specific_workout(workout_id, workout):
                ds_client.delete(workout.key)
                print("Finished deleting workout %s" % workout_id)


delete_workouts(None, None)
