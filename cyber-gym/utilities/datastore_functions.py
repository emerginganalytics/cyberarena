import time
import calendar
import random
import string
from yaml import load, Loader
from os import path, makedirs, remove
from google.cloud import datastore
from utilities.globals import ds_client, storage_client, workout_globals, project, BUILD_STATES
from werkzeug.utils import secure_filename
from utilities.assessment_functions import get_auto_assessment


def randomStringDigits(stringLength=10):
    return ''.join(random.choice(string.ascii_lowercase) for i in range(stringLength))


def add_server_defaults(servers):
    server_cnt = len(servers)
    for i in range(server_cnt):
        if 'build_type' not in servers[i]:
            servers[i]["build_type"] = None
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
        if 'add_disk' not in servers[i]:
            servers[i]["add_disk"] = None
        if 'include_env' not in servers[i]:
            servers[i]['include_env'] = False
        if 'operating-system' not in servers[i]:
            servers[i]['operating-system'] = None
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

    if 'student_entry' not in yaml_contents:
        yaml_contents['student_entry'] = None

    if yaml_contents['workout']['build_type'] == 'compute' or yaml_contents['workout']['build_type'] == 'arena':
        if 'routes' not in yaml_contents:
            yaml_contents['routes'] = None

        if yaml_contents['workout']['build_type'] == 'arena':
            yaml_contents['student-servers']['servers'] = add_server_defaults(yaml_contents['student-servers']['servers'])
            if 'additional-servers' in yaml_contents:
                yaml_contents['additional-servers'] = add_server_defaults(yaml_contents['additional-servers'])
            if 'student_entry_username' not in yaml_contents['student-servers']:
                yaml_contents['student-servers']['student_entry_username'] = None
            if 'student_entry_password' not in yaml_contents['student-servers']:
                yaml_contents['student-servers']['student_entry_password'] = None
        else:
            yaml_contents['servers'] = add_server_defaults(yaml_contents['servers'])

    return yaml_contents


def process_workout_yaml(yaml_contents, workout_type, unit_name, num_team, class_name, workout_length, email, unit_id=None):
    """
    Prepares the build of workouts based on a YAML specification by storing the information in the
    cloud datastore.
    :param yaml_contents: A string representation of a workout specification yaml
    :param workout_type: The name of the workout
    :param unit_name: A friendly name for the unit of workouts. A unit represents a classroom of students or teams
    :param num_team: The number of students or teams
    :param class_name: the name of the class 
    :param workout_length: The number of days this workout will remain in the cloud project.
    :param email: The email address of the instructor
    :param unit_id: The unit id for the workout to be assigned to for addition to a pre-existing unit
    :return: The unit_id AND the build type for the workout
    """
    y = load(yaml_contents, Loader=Loader)
    y = add_yaml_defaults(y)

    existing_unit = False
    if unit_id:
        existing_unit = True


    workout_name = y['workout']['name']
    build_type = y['workout']['build_type']
    workout_description = y['workout']['workout_description']
    teacher_instructions_url = None
    if y['workout']['teacher_instructions_url']:
        teacher_instructions_url = y['workout']['teacher_instructions_url']

    student_instructions_url = y['workout']['student_instructions_url']
    workout_url_path = y['workout']['workout_url_path']
    assessment = y['assessment']
    hourly_cost = None
    if 'hourly_cost' in y:
        hourly_cost = y['hourly_cost']
    if build_type == 'arena':
        student_servers = y['student-servers']['servers']
    if num_team:
        if num_team > workout_globals.max_num_workouts:
            num_team = workout_globals.max_num_workouts

    if int(workout_length) > workout_globals.max_workout_len:
        workout_length = workout_globals.max_workout_len

    workout_ids = []
    ts = str(calendar.timegm(time.gmtime()))
    if existing_unit:
        print("Building new workout for unit %s" % (unit_id))

    else:
        unit_id = randomStringDigits()
        print("Creating unit %s" % (unit_id))
        store_unit_info(id=unit_id, email=email, unit_name=unit_name, workout_name=workout_name, build_type=build_type,
                        ts=ts, workout_url_path=workout_url_path,
                        teacher_instructions_url=teacher_instructions_url, workout_description=workout_description)

    num_workouts = 0
    student_names = []
    if num_team:
        num_workouts = num_team
    else:
        class_list = ds_client.query(kind='cybergym-class')
        class_list.add_filter('teacher_email', '=', str(email))
        class_list.add_filter('class_name', '=', str(class_name))
        for class_object in list(class_list.fetch()): #Should return only a single class instance
            num_workouts = len(class_object['roster'])
            for student_name in class_object['roster']:
                student_names.append(student_name)
            unit_object = {
                "unit_id": str(unit_id),
                "unit_name": str(unit_name),
                "workout_name": str(workout_name),
                "build_type": str(build_type),
                "timestamp":str(ts)
            }
            
            if 'unit_list' not in class_object:
                unit_list = []
                unit_list.append(unit_object)
                class_object['unit_list'] = unit_list
            else:
                class_object['unit_list'].append(unit_object)
            ds_client.put(class_object)
    
    if build_type == 'container':
        container_info = y['container_info']
        for i in range(num_workouts):
            workout_id = randomStringDigits()
            workout_ids.append(workout_id)
            if student_names:
                store_workout_container(unit_id=unit_id, workout_id=workout_id, workout_type=workout_type,
                                    student_instructions_url=student_instructions_url,
                                    container_info=container_info, assessment=assessment, user_email=email, student_name=student_names[i])
            else:
                store_workout_container(unit_id=unit_id, workout_id=workout_id, workout_type=workout_type,
                                    student_instructions_url=student_instructions_url,
                                    container_info=container_info, assessment=assessment, user_email=email)
    elif build_type == 'compute':
        networks = y['networks']
        servers = y['servers']
        routes = y['routes']
        firewall_rules = y['firewall_rules']
        student_entry = y['student_entry']
        for i in range(num_workouts):
            workout_id = randomStringDigits()
            workout_ids.append(workout_id)
            if student_names:
                store_workout_info(workout_id=workout_id, unit_id=unit_id, user_mail=email,
                                workout_duration=workout_length, workout_type=workout_type,
                                networks=networks, hourly_cost=hourly_cost, servers=servers, routes=routes,
                                firewall_rules=firewall_rules, assessment=assessment,
                                student_instructions_url=student_instructions_url, student_entry=student_entry, student_name=student_names[i])
            else:
                store_workout_info(workout_id=workout_id, unit_id=unit_id, user_mail=email,
                                workout_duration=workout_length, workout_type=workout_type,
                                networks=networks, hourly_cost=hourly_cost, servers=servers, routes=routes,
                                firewall_rules=firewall_rules, assessment=assessment,
                                student_instructions_url=student_instructions_url, student_entry=student_entry)
                
    elif build_type == 'arena':
        networks = y['additional-networks'] if 'additional-networks' in y else None
        servers = y['additional-servers'] if 'additional-servers' in y else None
        routes = y['routes'] if 'routes' in y else None
        firewall_rules = y['firewall_rules']
        student_entry = y['student-servers']['student_entry']
        student_entry_type = y['student-servers']['student_entry_type']
        student_entry_username = y['student-servers']['student_entry_username']
        student_entry_password = y['student-servers']['student_entry_password']
        network_type = y['student-servers']['network_type']
        add_arena_to_unit(unit_id=unit_id, workout_duration=workout_length, timestamp=ts, networks=networks, user_mail=email,
                          servers=servers, routes=routes, firewall_rules=firewall_rules,
                          student_entry=student_entry, student_entry_type=student_entry_type, network_type=network_type,
                          student_entry_username=student_entry_username, student_entry_password=student_entry_password)
        for i in range(num_workouts):
            workout_id = randomStringDigits()
            workout_ids.append(workout_id)
            if student_names:
                store_arena_workout(workout_id=workout_id, unit_id=unit_id, student_servers=student_servers, user_mail=email,
                                    timestamp=ts, student_instructions_url=student_instructions_url, assessment=assessment, student_name=student_name[i])
            else:
                store_arena_workout(workout_id=workout_id, unit_id=unit_id, student_servers=student_servers, user_mail=email,
                                    timestamp=ts, student_instructions_url=student_instructions_url, assessment=assessment)
    

    unit = ds_client.get(ds_client.key('cybergym-unit', unit_id))
    if existing_unit:
        for temp_id in workout_ids:
            # unit['workouts'].append(temp_id)
            # ds_client.put(unit)
            return unit_id, build_type, temp_id
    else:
        unit['workouts'] = workout_ids
        unit['ready'] = True
        ds_client.put(unit)

        return unit_id, build_type


def store_workout_container(unit_id, workout_id, workout_type, student_instructions_url, container_info, assessment, user_email, student_name=None):
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
        'state': 'RUNNING',
        'user_email': user_email,
        'student_name': student_name
    })

    ds_client.put(new_workout)


def store_workout_info(workout_id, unit_id, user_mail, workout_duration, workout_type, networks, hourly_cost,
                       servers, routes, firewall_rules, assessment, student_instructions_url, student_entry, student_name=None):
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
        'complete': False,
        'student_entry': student_entry,
        'state': BUILD_STATES.START,
        'student_name': student_name, 
        'hourly_cost': hourly_cost
    })

    ds_client.put(new_workout)


# Store information for an individual unit.
def store_unit_info(id, email, unit_name, workout_name, build_type, ts, workout_url_path,
                    teacher_instructions_url, workout_description):
    new_unit = datastore.Entity(ds_client.key('cybergym-unit', id))

    new_unit.update({
        "unit_name": unit_name,
        "build_type": build_type,
        "workout_name": workout_name,
        "instructor_id": email,
        "timestamp": ts,
        'workout_url_path': workout_url_path,
        "description": workout_description,
        "teacher_instructions_url": teacher_instructions_url,
        "workouts": []
    })

    ds_client.put(new_unit)


def add_arena_to_unit(unit_id, workout_duration, timestamp, networks, user_mail, servers, routes, firewall_rules,
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


def store_arena_workout(workout_id, unit_id, user_mail, timestamp, student_servers, student_instructions_url,
                        assessment, student_name=None):
    new_workout = datastore.Entity(ds_client.key('cybergym-workout', workout_id))
    new_workout.update({
        'unit_id': unit_id,
        'type': 'arena',
        'build_type': 'arena',
        'student_instructions_url': student_instructions_url,
        'start_time': timestamp,
        'run_hours': 0,
        'timestamp': timestamp,
        'running': False,
        'misfit': False,
        'assessment': assessment,
        'student_servers': student_servers,
        'instructor_id': user_mail,
        'state': BUILD_STATES.START,
        'student_name':student_name
    })

    ds_client.put(new_workout)


# This function queries and returns all workout IDs for a given unit
def get_unit_workouts(unit_id):
    unit_workouts = ds_client.query(kind='cybergym-workout')
    unit_workouts.add_filter("unit_id", "=", unit_id)
    workout_list = []
    for workout in list(unit_workouts.fetch()):
        student_name = None
        if 'student_name' in workout:
            student_name = workout['student_name']
        if not student_name:
            student_name = ""
        # workout_instance = workout = ds_client.get(workout.key)
        state = None
        if 'state' in workout: 
            state = workout['state']

        submitted_answers = None
        if 'submitted_answers' in workout:
            submitted_answers = workout['submitted_answers']

        uploaded_files = None
        if 'uploaded_files' in workout:
            uploaded_files = workout['uploaded_files']

        auto_answers = get_auto_assessment(workout)
        workout_info = {
            'name': workout.key.name,
            'student_name': student_name,
            'state': state,
            'submitted_answers': submitted_answers,
            'uploaded_files': uploaded_files,
            'auto_answers': auto_answers
        }
        workout_list.append(workout_info)

    return workout_list

def get_unit_arenas(unit_id):
    unit_workouts = ds_client.query(kind='cybergym-workout')
    unit_workouts.add_filter("unit_id", "=", unit_id)
    workout_list = []
    for workout in list(unit_workouts.fetch()):
        student_name = None
        if 'student_name' in workout:
            student_name = workout['student_name']
        workout_instance = workout = ds_client.get(workout.key)
        state = None
        if 'state' in workout_instance: 
            state = workout_instance['state']

        team = None
        if 'team' in workout_instance:
            team = workout_instance['team']
        workout_info = {
            'name': workout.key.name,
            'student_name': student_name,
            'state': state,
            'teacher_email':workout['instructor_id'],
            'team': team
        }
        workout_list.append(workout_info)
    return workout_list



#store user submitted screenshots in cloud bucket
def store_student_uploads(workout_id, uploads):
    upload_bucket = str(project) + "_assessment_upload"
    bucket = storage_client.get_bucket(upload_bucket)
    for index, blob in enumerate(uploads):
        new_blob = bucket.blob(str(workout_id) + '/' + secure_filename(str(index)) + '.png')
        new_blob.upload_from_file(blob, content_type=blob.content_type)

def retrieve_student_uploads(workout_id):
    upload_bucket = str(project) + "_assessment_upload"
    bucket = storage_client.bucket(upload_bucket)
    file_list = []
    for blob in bucket.list_blobs():
        if str(workout_id) in blob.name:
            image_url = blob.public_url
            file_list.append(image_url)
    return file_list


def store_custom_logo(logo):
    bucket = storage_client.get_bucket(workout_globals.yaml_bucket)
    new_blob = bucket.blob('logo/logo.png')
    new_blob.cache_control = 'private'
    new_blob.upload_from_file(logo)

def store_background_color(color_code):
    css_string = ':root{--main_color: %s}' % (color_code)
    temp_css = open('temp.css', 'w')
    temp_css.write(css_string)
    temp_css.close()

    bucket = storage_client.get_bucket(workout_globals.yaml_bucket)
    new_blob = bucket.blob('color/{}-base.css'.format(project))
    #Prevent GCP from serving a cached version of this file
    new_blob.cache_control = 'private'
    new_blob.upload_from_string(css_string, content_type='text/css')

    remove('temp.css')

def add_new_teacher(teacher_email):
    new_teacher = datastore.Entity(ds_client.key('cybergym-instructor', teacher_email))
    # new_teacher['email'] = teacher_email
    ds_client.put(new_teacher)

def store_class_info(teacher_email, num_students, class_name):
    new_class = datastore.Entity(ds_client.key('cybergym-class'))

    new_class['teacher_email'] = teacher_email
    class_roster = []
    for i in range(int(num_students)):
        class_roster.append("Student {}".format(i+1))
    new_class['roster'] = class_roster
    new_class['class_name'] = class_name

    ds_client.put(new_class)

def upload_instruction_file(uploaded_file, folder, filename):
    bucket = storage_client.get_bucket(folder)
    new_blob = bucket.blob(filename)
    new_blob.cache_control = 'private'
    new_blob.upload_from_file(uploaded_file)

def store_comment(comment_email, comment_subject, comment_text):
    new_comment = datastore.Entity(ds_client.key('cybergym-comments'))
    new_comment['comment_email'] = comment_email
    new_comment['subject'] = comment_subject
    new_comment['comment_text'] = comment_text
    new_comment['message_viewed'] = False
    ds_client.put(new_comment)

def get_arena_ip_addresses_for_workout(workout_id):
    """
    Returns the server to local IP address mapping for a given arena and student workout. Not all servers have a
    direct guacamole connection, and the IP addresses are displayed to the student for jumping to other hosts
    from their landing server.
    :param workout_id: The Workout ID associated with the given arena
    """
    workout = ds_client.get(ds_client.key('cybergym-workout', workout_id))
    unit_id = workout['unit_id']
    arena_servers = []
    for server_spec in workout['student_servers']:
        server = ds_client.get(ds_client.key('cybergym-server', f"{workout_id}-{server_spec['name']}"))
        if server:
            server_to_ip = {'name': server_spec['name']}
            nics = []
            for interface in server['config']['networkInterfaces']:
                nic = {
                    'network': path.basename(interface['subnetwork']),
                    'ip': interface['networkIP']
                }
                nics.append(nic)
            server_to_ip['nics'] = nics
            arena_servers.append(server_to_ip)

    # Also include any additional shared servers in the arena
    unit = ds_client.get(ds_client.key('cybergym-unit', unit_id))
    if 'arena' in unit and 'servers' in unit['arena'] and unit['arena']['servers']:
        for server_spec in unit['arena']['servers']:
            server = ds_client.get(ds_client.key('cybergym-server', f"{unit_id}-{server_spec['name']}"))
            if server:
                server_to_ip = {'name': server['name']}
                nics = []
                for interface in server['config']['networkInterfaces']:
                    nic = {
                        'network': path.basename(interface['subnetwork']),
                        'ip': interface['networkIP']
                    }
                    nics.append(nic)
                server_to_ip['nics'] = nics
                arena_servers.append(server_to_ip)

    return arena_servers
