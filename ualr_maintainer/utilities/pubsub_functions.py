from google.cloud import pubsub_v1
# from common.globals import project

project = 'ualr-cybersecurity'
def pub_build_request_msg(workout_id):
    """
    Simple pub/sub message to build a workout specified through the workout_id in the Datastore object
    :param workout_id:
    :return:
    """
    topic_name = "build-workouts"

    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project, topic_name)

    data = "Cyber Gym Build Request"
    future = publisher.publish(topic_path, data=data.encode("utf-8"), workout_id=workout_id)

    print(future.result())


def pub_start_vm(workout_id):
    topic_name = "start-vm"

    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project, topic_name)

    data = "Cyber Gym VM Start Request"
    future = publisher.publish(topic_path, data=data.encode("utf-8"), workout_id=workout_id)

    print(future.result())


# pub_build_request_msg('cyberattack', '654321', '1', '1', 'pdhuff@ualr.edu', 'Testing')
pub_start_vm('1234')
