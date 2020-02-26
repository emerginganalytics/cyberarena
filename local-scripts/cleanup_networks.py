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
project = 'acapte'
zone = 'us-central1-a'
region = 'us-central1'
dnszone = 'cybergym-public'


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
    except(HttpError):
        print("Error in deleting subnetworks for %s" % workout_id)
        return False


def delete_network(workout_id):
    try:
        # First delete any routes specific to the workout
        result = compute.routes().list(project=project, filter='name = {}*'.format(workout_id)).execute()
        if 'items' in result:
            for route in result['items']:
                response = compute.routes().delete(project=project, route=route["name"]).execute()
            compute.globalOperations().wait(project=project, operation=response["id"]).execute()

 n       # Now it is safe to delete the networks.
        result = compute.networks().list(project=project, filter='name = {}*'.format(workout_id)).execute()
        if 'items' in result:
            for network in result['items']:
                compute.networks().delete(project=project, network=network["name"]).execute()
        return True
    except(HttpError):
        print("Error in deleting network for %s" % workout_id)
        return False


def delete_all_unused_networks():
    query_workouts = ds_client.query(kind='cybergym-workout')
    for workout in list(query_workouts.fetch()):
        expired_id = workout.key
        if delete_subnetworks(expired_id):
            if delete_network(expired_id):
                workout['resources_deleted'] = True



delete_all_unused_networks()