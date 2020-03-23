# Create Subscriber for each workout Topic
from google.cloud import pubsub_v1
import sys
import time

project_id = 'ualr-cybersecurity'


def create_subscriber(workout_id, workout_type):  # workout_topic = create_pub_sub_topic.topic_path
    subscriber = pubsub_v1.SubscriberClient()
    timeout = 10.0

    topic_name = '{}-{}-workout'.format(workout_id, workout_type)
    topic_path = subscriber.topic_path(project_id, topic_name)

    subscription = subscriber.subscription_path(
        project_id, topic_name
    )

    def callback(message):
        print("Received message: {}".format(message.data))
        if message.attributes:
            print("Attributes:")
            for key in message.attributes:
                value = message.attributes.get(key)
                print('{}: {}'.format(key, value))
        message.ack()

    streaming_pull_future = subscriber.subscribe(
        subscription, callback=callback
    )
    # If it doesn't exist, create subscription
    if not streaming_pull_future:
        subscription_path = subscriber.subscription_path(
            project_id, topic_name
        )
        create_subscription = subscriber.create_subscription(
            subscription_path, topic_path
        )
        streaming_pull_future = subscriber.subscribe(
            subscription, callback=callback
        )

    print("Listening for message on {}..\n".format(subscription))
    # subscription = subscriber.create_subscription(subscription_path, workout_topic)

    # If we get a message, break the loop; If false, retry in 3 minutes
    def pull_message():
        while True:
            try:
                streaming_pull_future.result(timeout=timeout)
            except Exception as e:
                print(
                   "Listening for messages on {} threw an exception: {}".format(topic_name, e)
                )
                streaming_pull_future.cancel()
                print('Pull canceled. Waiting 5 seconds ...')

                time.sleep(5)

    pull_message()


workout_id = sys.argv[1]
workout_type = sys.argv[2]

create_subscriber(workout_id, workout_type)
