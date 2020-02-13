# Simple Pub/Sub Script to check workout completion and return the flag
import sys
# TODO Establish Pub/Sub connection with workout based
#  functions

# Static Global Variables:
project_id = 'ualr-cybersecurity'
project_kind = 'cybergym-workout'

# Retrieving the flag from the GCP Datastore
def query_flag(workout_id):
    from google.cloud import datastore
    ds_client = datastore.Client()

    query = ds_client.query(kind=project_kind)
    for workout in list(query.fetch()):
        if workout['workout_ID'] == workout_id:
            return print(workout['flag'])


# for query testing purposes
# print(query_flag('pmljcz'))
def workouts(workout_type, workout_id):
    pass


def pub_sub(workout_name):
    from google.cloud import pubsub
    topic_name = '{}'.format(workout_name)

    publisher = pubsub.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_name)


# query_flag(sys.argv[1])
