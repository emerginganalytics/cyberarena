import time
import calendar
import random
import string
from yaml import load, Loader

from google.cloud import datastore
from globals import ds_client, storage_client, workout_globals


def randomStringDigits(stringLength=10):
    return ''.join(random.choice(string.ascii_lowercase) for i in range(stringLength))


def add_yaml_defaults(yaml_contents):
    """
    Add default values to the yaml. This prevents users from having to fully complete the yaml
    :param yaml_contents: A string representation of the yaml specification
    :return: A yaml_contents string with defaults added.
    """
    if 'build_type' not in yaml_contents['workout']:
        yaml_contents['workout']['build_type'] = 'compute'

    if 'workout_url_path' not in yaml_contents['workout']:
        yaml_contents['workout']['workout_url_path'] = None

    if "teacher_instructions_url" not in yaml_contents['workout']:
        yaml_contents['workout']['teacher_instructions_url'] = None

    if "student_instructions_url" not in yaml_contents['workout']:
        yaml_contents['workout']['student_instructions_url'] = None

    if 'workout_description' not in yaml_contents['workout']:
        yaml_contents['workout']['workout_description'] = None

    if 'container_info' not in yaml_contents:
        yaml_contents['container_info'] = None

    if yaml_contents['workout']['build_type'] == 'compute':
        if 'routes' not in yaml_contents:
            yaml_contents['routes'] = None

        server_cnt = len(yaml_contents['servers'])
        for i in range(server_cnt):
            if 'sshkey' not in yaml_contents['servers'][i]:
                yaml_contents['servers'][i]["sshkey"] = None
            if 'guac_path' not in yaml_contents['servers'][i]:
                yaml_contents['servers'][i]["guac_path"] = None
            if 'tags' not in yaml_contents['servers'][i]:
                yaml_contents['servers'][i]["tags"] = None
            if 'machine_type' not in yaml_contents['servers'][i]:
                yaml_contents['servers'][i]["machine_type"] = 'n1-standard-1'
            if 'network_routing' not in yaml_contents['servers'][i]:
                yaml_contents['servers'][i]["network_routing"] = False

    return yaml_contents


def process_workout_yaml(yaml_contents, workout_type, unit_name, num_team, workout_length, email):
    """
    Prepares the build of workouts based on a YAML specification by storing the information in the
    cloud datastore.
    :param yaml_contents: A string representation of a workout specification yaml
    :param workout_type: The name of the workout
    :param unit_name: A friendly name for the unit of workouts. A unit represents a classroom of students or teams
    :param num_team: The number of students or teams
    :param workout_length: The number of days this workout will remain in the cloud project.
    :param email: The email address of the instructor
    :return: The unit_id AND the build type for the workout
    """
    y = load(yaml_contents, Loader=Loader)
    y = add_yaml_defaults(y)
    unit_id = randomStringDigits()

    workout_name = y['workout']['name']
    build_type = y['workout']['build_type']
    workout_description = y['workout']['workout_description']
    teacher_instructions_url = y['workout']['teacher_instructions_url']
    student_instructions_url = y['workout']['student_instructions_url']
    workout_url_path = y['workout']['workout_url_path']


    # create random number specific to the workout (6 characters by default)
    if num_team > 10:
        num_team = 10

    if workout_length > 7:
        workout_length = 7

    # we have to store each labentry ext IP and send it to the user
    workout_ids = []

    ts = str(calendar.timegm(time.gmtime()))
    print("Creating unit %s" % (unit_id))
    store_unit_info(id=unit_id, email=email, unit_name=unit_name, workout_name=workout_name, build_type=build_type,
                    ts=ts, workout_type=workout_type, workout_url_path=workout_url_path,
                    teacher_instructions_url=teacher_instructions_url, workout_description=workout_description)

    if build_type == 'container':
        container_info = y['container_info']
        for i in range(1, num_team + 1):
            workout_id = randomStringDigits()
            workout_ids.append(workout_id)
            store_workout_container(unit_id=unit_id, workout_id=workout_id, workout_type=workout_type,
                                    student_instructions_url=student_instructions_url,
                                    container_info=container_info)
    elif build_type == 'compute':
        networks = y['networks']
        servers = y['servers']
        routes = y['routes']
        firewall_rules = y['firewall_rules']
        for i in range(1, num_team+1):
            workout_id = randomStringDigits()
            workout_ids.append(workout_id)
            store_workout_info(workout_id=workout_id, unit_id=unit_id, user_mail=email,
                               workout_duration=workout_length, workout_type=workout_type,
                               networks=networks, servers=servers, routes=routes, firewall_rules=firewall_rules)

    unit = ds_client.get(ds_client.key('cybergym-unit', unit_id))
    unit['workouts'] = workout_ids
    unit['ready'] = True
    ds_client.put(unit)

    return unit_id, build_type


def store_workout_container(unit_id, workout_id, workout_type, student_instructions_url, container_info):
    ts = str(calendar.timegm(time.gmtime()))
    new_workout = datastore.Entity(ds_client.key('cybergym-workout', workout_id))

    new_workout.update({
        'unit_id': unit_id,
        'build_type': 'container',
        'type': workout_type,
        'student_instructions_url': student_instructions_url,
        'timestamp': ts,
        'complete': False,
        'container_info': container_info
    })

    ds_client.put(new_workout)


def store_workout_info(workout_id, unit_id, user_mail, workout_duration, workout_type, networks,
                       servers, routes, firewall_rules):
    ts = str(calendar.timegm(time.gmtime()))
    new_workout = datastore.Entity(ds_client.key('cybergym-workout', workout_id))

    new_workout.update({
        'unit_id': unit_id,
        'user_email': user_mail,
        'expiration': workout_duration,
        'type': workout_type,
        'start_time': ts,
        'run_hours': 0,
        'timestamp': ts,
        'resources_deleted': False,
        'running': False,
        'misfit': False,
        'networks': networks,
        'servers': servers,
        'routes': routes,
        'firewall_rules': firewall_rules,
        'complete': False
    })

    ds_client.put(new_workout)


# Store information for an individual unit.
def store_unit_info(id, email, unit_name, workout_name, build_type, ts, workout_type, workout_url_path,
                    teacher_instructions_url, workout_description):
    new_unit = datastore.Entity(ds_client.key('cybergym-unit', id))

    new_unit.update({
        "unit_name": unit_name,
        "build_type": build_type,
        "workout_name": workout_name,
        "instructor_id": email,
        "timestamp": ts,
        "workout_type": workout_type,
        'workout_url_path': workout_url_path,
        "description": workout_description,
        "teacher_instructions_url": teacher_instructions_url,
        "workouts": [],
        "ready": False
    })

    ds_client.put(new_unit)


# This function queries and returns all workout IDs for a given unit
def get_unit_workouts(unit_id):
    unit_workouts = ds_client.query(kind='cybergym-workout')
    unit_workouts.add_filter("unit_id", "=", unit_id)
    workout_list = []
    for workout in list(unit_workouts.fetch()):
        workout_instance = workout = ds_client.get(workout.key)
        workout_info = {
            'name': workout.key.name,
            'running': workout_instance['running']
        }
        workout_list.append(workout_info)

    return workout_list
