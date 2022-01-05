import time
import calendar
import datetime
import random
import string
from yaml import load, Loader
from os import path, makedirs, remove
from google.cloud import datastore
from googleapiclient.errors import HttpError
from utilities.assessment_functions import get_auto_assessment
from utilities.globals import compute, ds_client, storage_client, workout_globals, project, dns_suffix, log_client, LOG_LEVELS, \
    BUILD_STATES, cloud_log
from utilities.workout_validator import WorkoutValidator
from werkzeug.utils import secure_filename


def add_additional_containers(containers):
    container_cnt = len(containers)
    for i in range(container_cnt):
        host_name = containers[i]['name']
        if 'path' not in containers[i]:
            containers[i]['container_url'] = f"http://{host_name}{dns_suffix}"
        else:
            path = containers[i]['path']
            containers[i]['container_url'] = f"http://{host_name}{dns_suffix}/{path}"
    return containers


def process_survey_yaml(yaml_contents):
    y = load(yaml_contents, Loader=Loader)
    return y
    

def store_student_feedback(feedback, workout_id):
    student_feedback = datastore.Entity(ds_client.key('cybergym-student-feedback', workout_id))
    
    for key in feedback.keys():
        student_feedback[key] = feedback[key]
    ds_client.put(student_feedback)
    print(student_feedback)
    return student_feedback


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

        assessment = workout.get('assessment', None)
        auto_answers = get_auto_assessment(workout)
        workout_info = {
            'name': workout.key.name,
            'student_name': student_name,
            'state': state,
            'submitted_answers': submitted_answers,
            'uploaded_files': uploaded_files,
            'auto_answers': auto_answers,
            'assessment': assessment
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
def store_student_upload(workout_id, upload, index):
    upload_bucket = str(project) + "_assessment_upload"
    bucket = storage_client.get_bucket(upload_bucket)
    new_blob = bucket.blob(str(workout_id) + '/' + secure_filename(str(index)) + '.png')
    new_blob.upload_from_file(upload, content_type=upload.content_type)
    return new_blob.public_url


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


def store_class_info(teacher_email, num_students, class_name, student_auth):
    new_class = datastore.Entity(ds_client.key('cybergym-class'))

    new_class['teacher_email'] = teacher_email
    class_roster = []
    for i in range(int(num_students)):
        class_roster.append("Student {}".format(i+1))
    new_class['roster'] = class_roster
    new_class['class_name'] = class_name
    new_class['student_auth'] = student_auth
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
    new_comment['date'] = datetime.datetime.now()
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
