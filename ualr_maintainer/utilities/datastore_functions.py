import time
import calendar
import random
import string
from yaml import load, Loader

from google.cloud import datastore
from globals import ds_client, storage_client, workout_globals


def randomStringDigits(stringLength=10):
    return ''.join(random.choice(string.ascii_lowercase) for i in range(stringLength))


def add_server_defaults(servers):
    server_cnt = len(servers)
    for i in range(server_cnt):
        if 'sshkey' not in servers[i]:
            servers[i]["sshkey"] = None
        if 'guac_path' not in servers[i]:
            servers[i]["guac_path"] = None
        if 'tags' not in servers[i]:
            servers[i]["tags"] = None
        if 'machine_type' not in servers[i]:
            servers[i]["machine_type"] = 'n1-standard-1'
        if 'network_routing' not in servers[i]:
            servers[i]["network_routing"] = False
        if 'nics' not in servers[i]:
            servers[i]['nics'] = None
    return servers


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

    if 'assessment' not in yaml_contents:
        yaml_contents['assessment'] = None

    if 'student-servers' not in yaml_contents:
        yaml_contents['student-servers'] = None

    if yaml_contents['workout']['build_type'] == 'compute' or yaml_contents['workout']['build_type'] == 'arena':
        if 'routes' not in yaml_contents:
            yaml_contents['routes'] = None

        if yaml_contents['workout']['build_type'] == 'arena':
            yaml_contents['additional-servers'] = add_server_defaults(yaml_contents['additional-servers'])
            yaml_contents['student-servers']['servers'] = add_server_defaults(yaml_contents['student-servers']['servers'])
            if 'student_entry_username' not in yaml_contents['student-servers']:
                yaml_contents['student-servers']['student_entry_username'] = None
            if 'student_entry_password' not in yaml_contents['student-servers']:
                yaml_contents['student-servers']['student_entry_password'] = None
        else:
            yaml_contents['servers'] = add_server_defaults(yaml_contents['servers'])

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
    if y['workout']['teacher_instructions_url']:
        teacher_instructions_url = y['workout']['teacher_instructions_url']
    elif y['workout']['instructor_instructions_url']:
        teacher_instructions_url = y['workout']['instructor_instructions_url']
    student_instructions_url = y['workout']['student_instructions_url']
    workout_url_path = y['workout']['workout_url_path']
    assessment = y['assessment']
    if build_type == 'arena':
        student_servers = y['student-servers']['servers']

    if num_team > workout_globals.max_num_workouts:
        num_team = workout_globals.max_num_workouts

    if workout_length > workout_globals.max_workout_len:
        workout_length = workout_globals.max_workout_len

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
                                    container_info=container_info, assessment=assessment)
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
                               networks=networks, servers=servers, routes=routes,
                               firewall_rules=firewall_rules, assessment=assessment,
                               student_instructions_url=student_instructions_url)
    elif build_type == 'arena':
        networks = y['additional-networks']
        servers = y['additional-servers']
        routes = y['routes']
        firewall_rules = y['firewall_rules']
        student_entry = y['student-servers']['student_entry']
        student_entry_type = y['student-servers']['student_entry_type']
        student_entry_username = y['student-servers']['student_entry_username']
        student_entry_password = y['student-servers']['student_entry_password']
        network_type = y['student-servers']['network_type']
        add_arena_to_unit(unit_id=unit_id, workout_duration=workout_length, timestamp=ts, networks=networks,
                          servers=servers, routes=routes, firewall_rules=firewall_rules,
                          student_entry=student_entry, student_entry_type=student_entry_type, network_type=network_type,
                          student_entry_username=student_entry_username, student_entry_password=student_entry_password)
        for i in range(1, num_team+1):
            workout_id = randomStringDigits()
            workout_ids.append(workout_id)
            store_arena_workout(workout_id=workout_id, unit_id=unit_id, student_servers=student_servers,
                                timestamp=ts, student_instructions_url=student_instructions_url, assessment=assessment)

    unit = ds_client.get(ds_client.key('cybergym-unit', unit_id))
    unit['workouts'] = workout_ids
    unit['ready'] = True
    ds_client.put(unit)

    return unit_id, build_type


def store_workout_container(unit_id, workout_id, workout_type, student_instructions_url, container_info, assessment):
    ts = str(calendar.timegm(time.gmtime()))
    new_workout = datastore.Entity(ds_client.key('cybergym-workout', workout_id))

    new_workout.update({
        'unit_id': unit_id,
        'build_type': 'container',
        'type': workout_type,
        'student_instructions_url': student_instructions_url,
        'timestamp': ts,
        'complete': False,
        'container_info': container_info,
        'assessment': assessment,
    })

    ds_client.put(new_workout)


def store_workout_info(workout_id, unit_id, user_mail, workout_duration, workout_type, networks,
                       servers, routes, firewall_rules, assessment, student_instructions_url):
    ts = str(calendar.timegm(time.gmtime()))
    new_workout = datastore.Entity(ds_client.key('cybergym-workout', workout_id))

    new_workout.update({
        'unit_id': unit_id,
        'user_email': user_mail,
        'student_instructions_url': student_instructions_url,
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
        'assessment': assessment,
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
        "workouts": []
    })

    ds_client.put(new_unit)


def add_arena_to_unit(unit_id, workout_duration, timestamp, networks, servers, routes, firewall_rules,
                      student_entry, student_entry_type, network_type, student_entry_username,
                      student_entry_password):
    """
    Adds the necessary build components to the unit to build a common network in which all students can interact.
    :param unit_id: The unit in which to add the arena build
    :param workout_duration: The number of days before deleting this arena
    :param start_time: Used for calculating how long an arena has run
    :param networks: The network to build for this arena
    :param servers: The servers to build for this arena
    :param routes: The routes to include for this arena
    :param firewall_rules: The firewall rules to add for the arena
    :param student_entry*: Parameters for building the guacamole connections through startup scripts
    :return: None
    """
    unit = ds_client.get(ds_client.key('cybergym-unit', unit_id))

    unit['arena'] = {
        'expiration': workout_duration,
        'start_time': timestamp,
        'run_hours': 0,
        'timestamp': timestamp,
        'resources_deleted': False,
        'running': False,
        'misfit': False,
        'networks': networks,
        'servers': servers,
        'routes': routes,
        'firewall_rules': firewall_rules,
        'student_entry': student_entry,
        'student_entry_type': student_entry_type,
        'student_entry_username': student_entry_username,
        'student_entry_password': student_entry_password,
        'student_network_type': network_type
    }

    ds_client.put(unit)


def store_arena_workout(workout_id, unit_id, timestamp, student_servers, student_instructions_url,
                        assessment):
    new_workout = datastore.Entity(ds_client.key('cybergym-workout', workout_id))

    new_workout.update({
        'unit_id': unit_id,
        'type': 'arena',
        'student_instructions_url': student_instructions_url,
        'start_time': timestamp,
        'run_hours': 0,
        'timestamp': timestamp,
        'running': False,
        'misfit': False,
        'assessment': assessment,
        'student_servers': student_servers,
    })

    ds_client.put(new_workout)


# This function queries and returns all workout IDs for a given unit
def get_unit_workouts(unit_id):
    unit_workouts = ds_client.query(kind='cybergym-workout')
    unit_workouts.add_filter("unit_id", "=", unit_id)
    workout_list = []
    for workout in list(unit_workouts.fetch()):

        workout_instance = workout = ds_client.get(workout.key)
        workout_info = {
            'name': workout.key.name,
            # 'running': workout_instance['running'],
            'complete': workout_instance['complete'],
        }
        workout_list.append(workout_info)

    return workout_list
