from google.cloud import pubsub_v1
from globals import ds_client, dns_suffix, project, compute, workout_globals, storage_client, logger

# TODO Identify where to call create_pub_sub_topic() and create_subscriber()
# Create Workout Topic Based on ID and Type[Name]
def create_workout_topic(workout_id, workout_type):
    publisher = pubsub_v1.PublisherClient()

    topic_name = '{}-{}-workout'.format(workout_id, workout_type)
    topic_path = publisher.topic_path(project, topic_name)

    topic = publisher.create_topic(topic_path)
    print('Topic created: {}'.format(topic))
    return topic_name


# Creates the Subscription for each Workout Topic
def create_subscription(topic_name):
    subscriber = pubsub_v1.SubscriberClient()

    # topic_name = '{}-{}-workout'.format(workout_id, workout_type)
    topic_path = subscriber.topic_path(project, topic_name)

    subscription_path = subscriber.subscription_path(
        project, topic_name
    )

    # TODO: move endpoint URL to globals
    endpoint = 'https://buildthewarrior.cybergym-eac-ualr.org/push'

    push_config = pubsub_v1.types.PushConfig(push_endpoint=endpoint)

    subscriber.create_subscription(
        subscription_path, topic_path, push_config
    )

    def callback(message):
        print("Received message: {}".format(message.data))
        if message.attributes:
            print("Attributes:")
            for key in message.attributes:
                value = message.attributes.get(key)
                print('{}: {}'.format(key, value))
        message.ack()

    future = subscriber.subscribe(subscription_path, callback)

    return subscription_path