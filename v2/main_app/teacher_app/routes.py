import logging as logger
import json
import time
from flask import Blueprint, redirect, render_template, request, session
from forms.forms import CreateWorkoutForm
from utilities.gcp.bucket_manager import BucketManager
from utilities.gcp.cloud_env import CloudEnv
from utilities.gcp.datastore_manager import DataStoreManager
from utilities.globals import DatastoreKeyTypes

teacher_app = Blueprint('teacher_app', __name__, url_prefix="/teacher",
                        static_folder="./static", template_folder="./templates")
# TODO: Move these to each call in teacher_api to the respective API route:
#  teacher_app.register_blueprint(teacher_api)


@teacher_app.route('/home', methods=['GET', 'POST'])
def teacher_home():
    auth_config = CloudEnv().auth_config
    if session.get('user_email', None):
        teacher_email = session['user_email']
        teacher_info = DataStoreManager(key_type=DatastoreKeyTypes.INSTRUCTOR,
                                            key_id=str(teacher_email)).get()
        if not teacher_info:
            # TODO: Add instructor to entity
            """teacher_info = DataStoreManager(key_id=DatastoreKeyTypes.INSTRUCTOR).query()
            teacher_list = list(teacher_info.fetch())
            DataStoreManager(key_id=str(teacher_email)).put(obj=teacher_email)"""
            teacher_info = teacher_email
        unit_query = DataStoreManager(key_id=DatastoreKeyTypes.CYBERGYM_UNIT.value).query()
        unit_query.add_filter('instructor_id', '=', str(teacher_email))
        unit_list = list(unit_query.fetch())
        class_list = DataStoreManager(key_id=str(teacher_email)).get_classroom()
        teacher_info = {}
        current_units = []
        expired_units = []
        teacher_classes = []
        for unit in unit_list:
            if 'workout_name' in unit:
                if 'expiration' in unit:
                    unit_info = {
                            'unit_id': unit.key.name,
                            'workout_name': unit['workout_name'],
                            'build_type': unit['build_type'],
                            'unit_name': unit['unit_name'],
                            'timestamp': unit['timestamp']
                        }
                    if (int(time.time()) - (int(unit['timestamp']) + ((int(unit['expiration'])) * 60 * 60 * 24))) < 0: 
                        current_units.append(unit_info)
                    else:
                        expired_units.append(unit_info)
                else:
                    unit_info = {
                            'unit_id': unit.key.name,
                            'workout_name': unit['workout_name'],
                            'build_type': unit['build_type'],
                            'unit_name': unit['unit_name'],
                            'timestamp': unit['timestamp']
                        }
                    expired_units.append(unit_info)
        current_units = sorted(current_units, key=lambda i: (i['timestamp']), reverse=True)
        expired_units = sorted(expired_units, key=lambda i: (i['timestamp']), reverse=True)
        for class_instance in class_list:
            if 'class_name' in class_instance:
                if 'student_auth' in class_instance:
                    auth_method = class_instance['student_auth']
                    if auth_method == 'email':
                        sorted_roster = sorted(class_instance['roster'], key=lambda k: k['student_name'])
                    else:
                        sorted_roster = sorted(class_instance['roster'])
                if 'unit_list' in class_instance:
                    class_unit_list = class_instance['unit_list']
                else:
                    class_unit_list = None
                class_info = {
                    'class_id': class_instance.id,
                    'class_name': class_instance['class_name'],
                    'roster': sorted_roster,
                    'student_auth': class_instance['student_auth'] if 'student_auth' in class_instance else 'anonymous',
                    'class_units': class_unit_list
                }
                teacher_classes.append(class_info)
        teacher_info['current_units'] = current_units
        teacher_info['expired_units'] = expired_units
        teacher_info['classes'] = teacher_classes

        # Get list of workouts from cloud bucket
        workout_build_options = BucketManager().get_workouts()
        return render_template('teacher_home.html', auth_config=auth_config, teacher_info=teacher_info,
                               workout_titles=workout_build_options)
    else:
        return redirect('/login')


@teacher_app.route('/<workout_type>', methods=['GET'])
def index(workout_type):
    auth_config = CloudEnv().auth_config
    logger.info('Request for workout type %s' % workout_type)
    form = CreateWorkoutForm()
    return render_template('main_page.html', workout_type=workout_type, auth_config=auth_config)


# Instructor landing page. Displays information and links for a unit of workouts
@teacher_app.route('/workout_list/<unit_id>', methods=['GET', 'POST'])
def workout_list(unit_id):
    ds_manager = DataStoreManager(key_type=DatastoreKeyTypes.CYBERGYM_UNIT, key_id=str(unit_id))
    unit = ds_manager.get()
    build_type = unit['build_type']
    workout_list = DataStoreManager().get_workouts()
    registration_required = unit.get('registration_required', False)
    if not registration_required:
        workout_list = sorted(workout_list, key=lambda i: (i['student_name']))
    else:
        workout_list = sorted(workout_list, key=lambda i: (i['student_name']['student_name']))
    teacher_instructions_url = None
    if 'teacher_instructions_url' in unit:
        teacher_instructions_url = unit['teacher_instructions_url']

    attack_yaml = DataStoreManager().get_attack_specs()
    # For updating individual workout ready state
    if request.method=="POST":
        if build_type == 'arena':
            return json.dumps(unit)
        return json.dumps(workout_list)

    if unit and len(str(workout_list)) > 0:
        return render_template('workout_list.html', workout_list=workout_list, unit=unit,
                               teacher_instructions=teacher_instructions_url, main_app_url=CloudEnv().main_app_url,
                               attack_spec=attack_yaml)
    else:
        return redirect('/no-workout')


@teacher_app.route('/arena_list/<unit_id>', methods=['GET', 'POST'])
def arena_list(unit_id):
    # Get Arena Datastore objects
    unit_query = DataStoreManager(key_type=DatastoreKeyTypes.CYBERGYM_UNIT, key_id=str(unit_id))
    unit = unit_query.get()
    workout_list = DataStoreManager().get_workouts()
    teacher_instructions_url = None
    if 'teacher_instructions_url' in unit:
        teacher_instructions_url = unit['teacher_instructions_url']
    student_instructions_url = None
    if 'student_instructions_url' in unit:
        student_instructions_url = unit['student_instructions_url']

    start_time = None
    if'start_time' in unit:
        start_time = unit['start_time']
        # start_time = time.gmtime(start_time)
    unit_teams = None
    if 'teams' in unit:
        unit_teams = unit['teams']

    if request.method == "POST":
        return json.dumps(unit)
    if unit:
        return render_template('arena_list.html', unit_teams=unit_teams, teacher_instructions=teacher_instructions_url,
                               workout_list=workout_list, student_instructions=student_instructions_url,
                               description=unit['description'], unit_id=unit_id, start_time=start_time)
