#
# This script is intended to be copied into the landing page application for the button click when
# resuming a workout which has previously been stopped.
#
import calendar
import googleapiclient.discovery
import time
from common.globals import BUILD_STATES, compute, dnszone, dns_suffix, ds_client, log_client, LOG_LEVELS, project, \
    PUBSUB_TOPICS, SERVER_ACTIONS, workout_globals
from common.state_transition import state_transition
from google.cloud import pubsub_v1
from googleapiclient.errors import HttpError

# Global variables for this function
expired_workout = []


def start_vm(workout_id):
    g_logger = log_client.logger(str(workout_id))
    g_logger.log_struct(
        {
            "message": "Starting workout {}".format(workout_id)
        }, severity=LOG_LEVELS.INFO
    )
    # print("Starting workout %s" % workout_id)
    workout = ds_client.get(ds_client.key('cybergym-workout', workout_id))
    state_transition(entity=workout, new_state=BUILD_STATES.STARTING)
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


def start_arena(unit_id):
    g_logger = log_client.logger('arena-actions')
    g_logger.log_struct(
        {
            "message": "Starting arena {}".format(unit_id)
        }, severity=LOG_LEVELS.INFO
    )
    
    unit = ds_client.get(ds_client.key('cybergym-unit', unit_id))
    state_transition(entity=unit, new_state=BUILD_STATES.STARTING)
    unit['arena']['running'] = True
    unit['arena']['gm_start_time'] = str(calendar.timegm(time.gmtime()))
    ds_client.put(unit)

    # Start the central servers
    g_logger.log_struct(
        {
            "message": "Starting central servers for arena {}".format(unit_id)
        }, severity=LOG_LEVELS.INFO
    )
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
