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
    """
    This is necessary because the network does not always delete. The routes take a while to clear from the GCP.
    :param network: The network name to delete
    :param response: The last response from globalOperations.get()
    :return: Boolean on whether the network delete was successful.
    """
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
            time.sleep(5)
            if delete_firewall_rules(workout_id):
                time.sleep(5)
                if delete_subnetworks(workout_id):
                    time.sleep(5)
                    if delete_network(workout_id):
                        return True

        return False


def delete_specific_arena(unit_id, unit):
    """
    Arenas are unique in having both resources at the unit level and individual workout resources. This
    function addresses those differences
    :param arena_id: The Unit_ID of this arena
    :return:
    """
    try:
        delete_dns(unit_id, unit["external_ip"])
    except HttpError:
        print("DNS record does not exist")
        pass
    except KeyError:
        print("workout %s has no external IP address" % unit_id)
        pass
    
    # First delete all servers associated with this unit
    delete_vms(unit_id)
    for workout_id in unit['workouts']:
        delete_vms(workout_id)
    time.sleep(5)
    # Now delete all of the network elements
    delete_firewall_rules(unit_id)
    for workout_id in unit['workouts']:
        delete_firewall_rules(workout_id)
    time.sleep(5)
    delete_subnetworks(unit_id)
    for workout_id in unit['workouts']:
        delete_subnetworks(workout_id)
    time.sleep(5)
    delete_network(unit_id)
    for workout_id in unit['workouts']:
        delete_network(workout_id)
    return True


def delete_workouts():
    """
    Queries the data store for workouts which have expired. Workout expiration is defined during the build
    process based on the number of days an instructor needs the workout to be available. Resources to delete include
    servers, networks, routes, firewall-rules and DNS names. The deletion of resources is based on a unique
    identifier for the workout. Every built resource uses this for a prefix.
    Deletion must occur in a given order with networks being deleted last.

    There is also a mechanism to delete what we refer to as misfit workouts. This is simply a boolean in the data store
    to indicate when a workout was created by a mistake or some other error in processing.

    This function is intended to be consumed through cloud_fn_delete_expired_workout and tied to a pubsub topic
    triggered by a cloud scheduler to run every 15 minutes or more.
    :return: None
    """
    # Only process the workouts from the last 4 months. 10512000 is the number of seconds in a month
    query_old_workouts = ds_client.query(kind='cybergym-workout')
    query_old_workouts.add_filter("timestamp", ">", str(calendar.timegm(time.gmtime()) - 10512000))
    for workout in list(query_old_workouts.fetch()):
        if 'resources_deleted' not in workout:
            workout['resources_deleted'] = False

        container_type = False
        if 'build_type' in workout and workout['build_type'] == 'container':
            container_type = True

        arena_type = False
        if 'build_type' in workout and workout['build_type'] == 'arena':
            arena_type = True

        if not container_type and not arena_type and 'expiration' in workout:
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


def delete_arenas():
    """
    It is common for cloud functions to time out when deleting several workouts. This adds an additional work thread
    to delete arenas similar to the delete_workouts() function
    :return:
    """
    query_old_units = ds_client.query(kind='cybergym-unit')
    query_old_units.add_filter("timestamp", ">", str(calendar.timegm(time.gmtime()) - 10512000))
    for unit in list(query_old_units.fetch()):
        arena_type = False
        if 'build_type' in unit and unit['build_type'] == 'arena':
            arena_type = True

        if arena_type:
            try:
                arena = unit['arena']
                if workout_age(arena['timestamp']) >= int(arena['expiration']) \
                        and not arena['resources_deleted']:
                    arena_id = unit.key.name
                    print('Deleting resources from arena %s' % arena_id)
                    if delete_specific_arena(arena_id, unit):
                        arena['resources_deleted'] = True
                        ds_client.put(unit)
            except KeyError:
                unit['arena'] = {'resources_deleted': True}
                ds_client.put(unit)

    # Delete any misfit arenas
    query_misfit_arenas = ds_client.query(kind='cybergym-unit')
    query_misfit_arenas.add_filter("misfit", "=", True)
    for unit in list(query_misfit_arenas.fetch()):
        arena_id = unit.key.name

        print('Deleting resources from arena %s' % arena_id)
        if delete_specific_arena(arena_id, unit):
            ds_client.delete(unit.key)
            print("Finished deleting arena %s" % arena_id)

# delete_workouts()
# delete_arenas()
