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


def delete_specific_network(workout_id):
    print('Beginning network delete for %s' % workout_id)
    if delete_firewall_rules(workout_id):
        if delete_subnetworks(workout_id):
            if delete_network(workout_id):
                return True
    return False


# The main function is only for debugging. Do not include this line in the cloud function
# delete_workouts(None, None)
specific_workouts = ['zhwruu', 'zwivew']
for workout in specific_workouts:
    delete_specific_network(workout)