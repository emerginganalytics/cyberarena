#
# This script is intended to be copied into the landing page application for the button click when
# resuming a workout which has previously been stopped.
#
import googleapiclient.discovery
import time
import calendar
from googleapiclient.errors import HttpError
from google.cloud import pubsub_v1

from common.state_transition import state_transition
from common.globals import ds_client, project, compute, dnszone, dns_suffix, workout_globals, BUILD_STATES, \
    PUBSUB_TOPICS, SERVER_ACTIONS
from common.dns_functions import add_dns_record
from common.prepare_compute import get_server_ext_address
from common.compute_management import server_start

# Global variables for this function
expired_workout = []
zone = 'us-central1-a'
region = 'us-central1'


# Create a new DNS record for the server and add the information to the datastore for later management
def register_workout_update(project, dnszone, workout_id, new_ip):
    service = googleapiclient.discovery.build('dns', 'v1')

    # First, get the existing workout DNS
    response = service.resourceRecordSets().list(project=project, managedZone=dnszone,
                                              name=workout_id + dns_suffix + ".").execute()
    existing_rrset = response['rrsets']
    change_body = {
        "deletions": existing_rrset,
        "additions": [
            {
                "kind": "dns#resourceRecordSet",
                "name": workout_id + dns_suffix + ".",
                "rrdatas": [new_ip],
                "type": "A",
                "ttl": 30
            }
    ]}

    # Try first to perform the DNS change, but in case the DNS did not previously exist, try again without the deletion change.
    try:
        request = service.changes().create(project=project, managedZone=dnszone, body=change_body).execute()
    except HttpError:
        try:
            del change_body["deletions"]
            request = service.changes().create(project=project, managedZone=dnszone, body=change_body).execute()
        except HttpError:
            # Finally, it may be the DNS has already been successfully updated, in which case
            # the API call will throw an error. We ignore this case.
            pass

    # Now update the parameters in the workout object
    key = ds_client.key('cybergym-workout', workout_id)
    workout = ds_client.get(key)
    workout["external_ip"] = new_ip

    ds_client.put(workout)


def start_vm(workout_id):
    print("Starting workout %s" % workout_id)
    workout = ds_client.get(ds_client.key('cybergym-workout', workout_id))
    state_transition(entity=workout, new_state=BUILD_STATES.STARTING)
    workout['running'] = True
    workout['start_time'] = str(calendar.timegm(time.gmtime()))
    ds_client.put(workout)

    query_workout_servers = ds_client.query(kind='cybergym-server')
    query_workout_servers.add_filter("workout", "=", workout_id)
    for server in list(query_workout_servers.fetch()):
        # Publish to a server management topic
        pubsub_topic = PUBSUB_TOPICS.MANAGE_SERVER
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(project, pubsub_topic)
        future = publisher.publish(topic_path, data=b'Server Build', server_name=server['name'],
                                   action=SERVER_ACTIONS.START)
        print(future.result())
    state_transition(entity=workout, new_state=BUILD_STATES.RUNNING)


def start_arena(unit_id):
    print("Starting arena %s" % unit_id)
    unit = ds_client.get(ds_client.key('cybergym-unit', unit_id))
    state_transition(entity=unit, new_state=BUILD_STATES.STARTING)
    unit['arena']['running'] = True
    unit['arena']['gm_start_time'] = str(calendar.timegm(time.gmtime()))
    ds_client.put(unit)


    # Start the central servers
    print(f"Starting central servers for the arena with unit ID {unit_id}")
    query_central_arena_servers = ds_client.query(kind='cybergym-server')
    query_central_arena_servers.add_filter("workout", "=", unit_id)
    for server in list(query_central_arena_servers.fetch()):
        # Publish to a server management topic
        pubsub_topic = PUBSUB_TOPICS.MANAGE_SERVER
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(project, pubsub_topic)
        future = publisher.publish(topic_path, data=b'Server Build', server_name=server['name'],
                                   action=SERVER_ACTIONS.START)
        print(future.result())

    # Now start all of the student workouts for this arena
    for workout_id in unit['workouts']:
        start_vm(workout_id)
    state_transition(entity=unit, new_state=BUILD_STATES.RUNNING)


# start_arena('wsojiwqdqg')