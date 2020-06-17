from google.cloud import pubsub_v1
from google.cloud.pubsub import types

from utilities.datastore_functions import get_unit_workouts
from time import sleep

# from common.globals import project

project = 'ualr-cybersecurity'
def pub_build_request_msg(unit_id, topic_name='build-workouts'):
    """
    Simple pub/sub message to build a workout specified through the workout_id in the Datastore object
    :param workout_id:
    :return:
    """
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project, topic_name)

    if topic_name == 'build_workouts':
        workouts = get_unit_workouts(unit_id)
        for workout in workouts:
            future = publisher.publish(topic_path, data=b'Cyber Gym Workout', workout_id=workout['name'])
            print(future.result())
    elif topic_name == 'build_arena':
        future = publisher.publish(topic_path, data=b'Cyber Gym Arena', unit_id=unit_id)
        print(future.result())


def pub_start_vm(build_id, topic_name='start-vm'):
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project, topic_name)

    if topic_name == 'start-vm':
        data = "Cyber Gym VM Start Request"
        future = publisher.publish(topic_path, data=data.encode("utf-8"), workout_id=build_id)
    elif topic_name == 'start-arena':
        data = 'Cyber Gym Arena Start Request'
        future = publisher.publish(topic_path, data=data.encode("utf-8"), unit_id=build_id)

    print(future.result())


# pub_build_request_msg('cyberattack', '654321', '1', '1', 'pdhuff@ualr.edu', 'Testing')
pub_start_vm('1234')

