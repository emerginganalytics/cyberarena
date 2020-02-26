import googleapiclient.discovery
from datetime import datetime, timedelta, date
from google.cloud import datastore
import time
import calendar
from googleapiclient.errors import HttpError

# Global variables for this function
ds_client = datastore.Client()
compute = googleapiclient.discovery.build('compute', 'v1', cache_discovery=False)
expired_workout = []
project = 'ualr-cybersecurity'
zone = 'us-central1-a'
region = 'us-central1'
dnszone = 'cybergym-public'


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
    except(HttpError):
        print("Error in deleting subnetworks for %s" % workout_id)
        return False
    return True


# The only way I found that works to test the emptiness of a network is trying to delete it.
# To avoid deleting firewall rules, if the first delete works, then I know its empty and can
# delete all of the firewall rules. Then I can delete the network.
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
                delete_firewall_rules(workout_id)
                try:
                    compute.networks().delete(project=project, network=network["name"]).execute()
                except HttpError:
                    pass
    except HttpError:
        print("Error in deleting network for %s" % workout_id)
        return False
    return True


# This script is sloppy, but I needed it in a pinch. Need to test and determine which networks still have servers
# in them.
def delete_all_unused_networks():
    query_workouts = ds_client.query(kind='cybergym-workout')
    query_workouts.add_filter("timestamp", ">", str(calendar.timegm(time.gmtime()) - 2628000))
    for workout in list(query_workouts.fetch()):
        workout_id = workout.key.name
        print("Processing workout: %s" % workout_id)
        delete_subnetworks(workout_id)
        delete_network(workout_id)



delete_all_unused_networks()