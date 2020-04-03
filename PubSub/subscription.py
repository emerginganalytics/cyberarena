# Create Subscriber for each workout Topic
from google.cloud import pubsub_v1
import sys
import time

subscriber = pubsub_v1.SubscriberClient()

project_id = 'ualr-cybersecurity'
workout_id = sys.argv[1]
workout_type = sys.argv[2]
timeout = 10.0
topic_name = '{}-{}-workout'.format(workout_id, workout_type)
topic_path = subscriber.topic_path(project_id, topic_name)

subscription = subscriber.subscription_path(
    project_id, topic_name
)

def callback(message):
    print("[+] Received message: {}".format(message.data))
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

print("[*] Listening for message on {}..\n".format(subscription))

with subscriber:
    try:
        streaming_pull_future.result(timeout=timeout)
    except Exception as e:
        streaming_pull_future.cancel()
        print(
            "[+] Listening for messages on {} threw an exception: {}.".format(subscription, e)
        )
