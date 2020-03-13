# Simple Pub/Sub Script to establish Pub/Sub system and return the flag
# TODO Establish Pub/Sub connection with workout based
#  functions.
# TODO Build conditional script on each workout server
#  that will check for completion before publishing to
#  related topic. Ex: 1 hiddennode publishes to
#  ad8jds-hiddennode-workout
from google.cloud import pubsub_v1
import base64 as b64
import sys

# Retrieves the flag from the GCP Datastore
# Will be implemented into Student Landing
# page NOT pub/sub server
class Info:
    # Project variables
    project_id = 'ualr-cybersecurity'
    project_kind = 'cybergym-workout'

    # Topic Variables
    topic_name = ''
    topic_path = ''
    topic = ''

    # Subscription variables
    subscription_path = ''
    subscription = ''

    # Workout Variables
    workout_name = ''
    workout_id = ''

# not needed since page already uses this
def query_flag(workout_id):
    from google.cloud import datastore
    ds_client = datastore.Client()

    query = ds_client.query(kind=Info.project_kind)
    for workout in list(query.fetch()):
        if workout['workout_ID'] == workout_id:
            return workout['flag']


# Create a topic for each workout built based on workout id and type (name):
# [!!] Initially Created with web app as the publisher
def create_pub_sub(workout_id, workout_name, pub_message):
    Info.topic_name = '{}-{}-workout'.format(workout_id, workout_name)

    publisher = pubsub_v1.PublisherClient()
    Info.topic_path = publisher.topic_path(Info.project_id, Info.topic_name)

    topic = publisher.create_topic(Info.topic_path)
    Info.topic = topic
    print("Topic created: {}".format(topic))

    print("Topic_name = {}".format(Info.topic_name))
    print("Topic_path = {}".format(Info.topic_path))
    print("Topic = {}".format(Info.topic))

    publisher.publish(Info.topic_path, pub_message, spam='eggs')
    print('[+] Publishing Message to {}...'.format(topic))


# Creates a Pull subscription. Possibly need to reformat to Push subscription
#  with CybergGym endpoint POST URL
def create_subscription(sub_message):
    # Create a Pull Subscription for the workout topic
    print('[+] Creating subscriber ...')
    subscriber = pubsub_v1.SubscriberClient()
    topic_path = subscriber.topic_path(Info.project_id, Info.topic_name)

    # sub_path requires project_id and subscription_name(sub_name == topic_name)
    # Set and Create Subscription path
    subscription_path = subscriber.subscription_path(Info.project_id, Info.topic_name)
    subscription = subscriber.create_subscription(subscription_path, topic_path)

    # Update Class Info member values
    Info.subscription_path = subscription_path
    Info.subscription = subscription

    print('[*] Pull Subscription created: {}'.format(subscription))
    print('Subscription_path = {}'.format(subscription_path))
    print('subscription = {}'.format(subscription))
    def callback(sub_message):
        print('[*] Received message: {}'.format(sub_message.data))
        if sub_message.attributes:
            print("[*] Attributes:")
            for key in sub_message.attributes:
                value = sub_message.attributes.get(key)
                print("[-->] {}: {}".format(key, value))
        sub_message.ack()

    streaming_pull_future = subscriber.subscribe(
        subscription_path, callback=callback
    )
    print('[*] Listening for messages on {}...\n'.format(subscription_path))

    # result() in a future will block indefinitely if 'timeout' is not set,
    # unless an exception is encountered first.
    try:
        streaming_pull_future.result(timeout=5.0)
    except:     # noqa
        streaming_pull_future.cancel()
    return Info.topic, subscription


# [!!] Following portions are for local testing purposes only [!!]
def delete_pubsub():
    # Code to Delete Topic
    publisher = pubsub_v1.PublisherClient()
    publisher.delete_topic('projects/ualr-cybersecurity/topics/promise-permissions-workout')

    print("[*] Topic deleted: {}".format('projects/ualr-cybersecurity/topics/promise-permissions-workout'))

    # Code to Delete Subscription
    subscriber = pubsub_v1.SubscriberClient()
    subscriber.delete_subscription('projects/ualr-cybersecurity/subscriptions/-vnc-permissions')

    print("[*] Subscription deleted: {}".format('projects/ualr-cybersecurity/topics/-vnc-permissions'))


# Testing Calls
pub_message = b64.b64encode(b"Linux is complete")
sub_message = b64.b64encode(b"I'm a subscriber!")

Info.workout_id = 'promise'
Info.workout_name = 'permissions'

if sys.argv[1] == 'create':
    create_pub_sub(Info.workout_id, Info.workout_name, pub_message)
    create_subscription(sub_message)
elif sys.argv[1] == 'delete':
    delete_pubsub()
else:
    print('Invalid: Use create or delete')
