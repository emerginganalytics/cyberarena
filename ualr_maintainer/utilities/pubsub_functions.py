from google.cloud import pubsub_v1
from common.globals import project


def pub_build_request_msg(workout, unit_id, num_team, length, email, unit_name):
    """ Publishes to the project pubsub topic build-workouts, which gets processed by
        a cloud function to build the designated workout.
    Args:
         The parameters are the minimal necessary to build a new workout for a class.
    """
    topic_name = "build-workouts"

    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project, topic_name)

    data = "Cyber Gym Build Request"
    future = publisher.publish(topic_path, data=data.encode("utf-8"),
                      workout=workout,
                      unit_id=unit_id,
                      num_team=str(num_team),
                      length=str(length),
                      email=email,
                      unit_name=unit_name)

    print(future.result())


pub_build_request_msg('cyberattack', '654321', '1', '1', 'pdhuff@ualr.edu', 'Testing')