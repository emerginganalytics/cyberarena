from google.cloud import pubsub_v1

from utilities.globals import workout_globals, project, ds_client
from utilities.datastore_functions import get_unit_workouts


class PUBSUB_TOPICS:
    MANAGE_SERVER = 'manage-server'
    BUILD_WORKOUTS = 'build-workouts'
    ADMIN_SCRIPTS = 'admin-scripts'


class WORKOUT_ACTIONS:
    BUILD = 'BUILD'
    NUKE = 'NUKE'


def pub_build_request_msg(unit_id, topic_name):
    """
    Simple pub/sub message to build a workout specified through the workout_id in the Datastore object
    :param workout_id:
    :return:
    """
    publisher = pubsub_v1.PublisherClient()

    if topic_name == workout_globals.ps_build_workout_topic:
        workouts = get_unit_workouts(unit_id)
        for workout in workouts:
            build_project_location = workout.get('build_project_location', project)
            topic_path = publisher.topic_path(build_project_location, topic_name)
            future = publisher.publish(topic_path, data=b'Cyber Gym Workout', workout_id=workout['name'])
            print(future.result())
    elif topic_name == workout_globals.ps_build_arena_topic:
        topic_path = publisher.topic_path(project, topic_name)
        future = publisher.publish(topic_path, data=b'Cyber Gym Arena', unit_id=unit_id)
        print(future.result())


def pub_start_vm(build_id, topic_name='start-vm'):
    publisher = pubsub_v1.PublisherClient()

    if topic_name == 'start-vm':
        workout = ds_client.get(ds_client.key('cybergym-workout', build_id))
        build_project_location = workout.get('build_project_location', project)
        topic_path = publisher.topic_path(build_project_location, topic_name)
        data = "Cyber Gym VM Start Request"
        future = publisher.publish(topic_path, data=data.encode("utf-8"), workout_id=build_id)
    elif topic_name == 'start-arena':
        topic_path = publisher.topic_path(project, topic_name)
        data = 'Cyber Gym Arena Start Request'
        future = publisher.publish(topic_path, data=data.encode("utf-8"), unit_id=build_id)

    print(future.result())


def pub_stop_vm(workout_id, topic_name='stop-vm'):
    publisher = pubsub_v1.PublisherClient()
    workout = ds_client.get(ds_client.key('cybergym-workout', workout_id))
    build_project_location = workout.get('build_project_location', project)
    topic_path = publisher.topic_path(build_project_location, topic_name)
    data = 'Cyber Gym VM Stop Request'
    publisher.publish(topic_path, data=data.encode('utf-8'), workout_id=workout_id)


def pub_manage_server(server_name, action, topic_name="manage-server"):
    server = ds_client.get(ds_client.key('cybergym-server', server_name))
    workout_id = server.get('workout', None)
    workout = ds_client.get(ds_client.key('cybergym-workout', workout_id))
    build_project_location = workout.get('build_project_location', project)

    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(build_project_location, topic_name)
    publisher.publish(topic_path, data=b'Server Build', action=action.encode('utf-8'), server_name=server_name)


def pub_nuke_workout(workout_id):
    workout = ds_client.get(ds_client.key('cybergym-workout', workout_id))
    build_project_location = workout.get('build_project_location', project)

    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(build_project_location, PUBSUB_TOPICS.BUILD_WORKOUTS)
    data = "Workout nuke and rebuild request"
    publisher.publish(topic_path, data=data.encode("utf-8"), workout_id=workout_id, action=WORKOUT_ACTIONS.NUKE)


def pub_admin_scripts(script_dict):
    """
    Pubsub message to use admin scripts for easy maintenance / upkeep
    :param script_dict: contains info for the name of the script to run, as well as any parameters that the script requires
        Formatted as {function_name: <ADMIN_SCRIPT_NAME>, params: {<script_param1>: param_value, <script_param2>: param2_value}}
    """
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project, PUBSUB_TOPICS.ADMIN_SCRIPTS)
    data = "Admin scripts for easy access to maintenance functions"
    publisher.publish(topic_path, data=data.encode('utf-8'), script_dict=str(script_dict))