from google.cloud import pubsub_v1
from google.cloud import datastore
from globals import project, ds_client
import base64 as b64

# sub('PLEKNG')
def test_subscription(topic_name):
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
                status = message.attributes.get('workout_id')
                if status:
                    workout_table = datastore.Entity(ds_client.key('cybergym-workout', status))
                    workout_table.update({'complete': True})
        message.ack()

    future = subscriber.subscribe(subscription_path, callback)

    return subscription_path