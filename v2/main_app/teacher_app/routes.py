import logging as logger
import json
import time
from flask import abort, Blueprint, redirect, render_template, request, session
from forms.forms import CreateWorkoutForm
from main_app_utilities.gcp.arena_authorizer import ArenaAuthorizer
from main_app_utilities.gcp.bucket_manager import BucketManager
from main_app_utilities.gcp.cloud_env import CloudEnv
from main_app_utilities.gcp.datastore_manager import DataStoreManager
from main_app_utilities.globals import DatastoreKeyTypes

teacher_app = Blueprint('teacher_app', __name__, url_prefix="/teacher",
                        static_folder="./static", template_folder="./templates")

auth_config = CloudEnv().auth_config


@teacher_app.route('/home', methods=['GET', 'POST'])
def teacher_home():
    if session.get('user_email', None):
        teacher_email = session['user_email']
        auth = ArenaAuthorizer()
        auth_list = auth.get_user_groups(user=teacher_email)  # Get user auth levels
        # Check if teacher is added to datastore
        teacher_info = DataStoreManager(key_type=DatastoreKeyTypes.INSTRUCTOR, key_id=str(teacher_email)).get()
        if not teacher_info:
            teacher_info = DataStoreManager().set(key_type=DatastoreKeyTypes.INSTRUCTOR, key_id=str(teacher_email))
            # TODO: Add instructor to entity

        teacher_info = {}
        """teacher_classes = []
        class_list = DataStoreManager(key_id=str(teacher_email)).get_classrooms()
        for class_instance in class_list:
            if 'class_name' in class_instance:
                class_info = {
                    'id': class_instance['class_id'],
                    'name': class_instance['class_name'],
                    'student_auth': class_instance['student_auth'] if 'student_auth' in class_instance else 'anonymous',
                    'roster_size': len(class_instance.get('roster', []))
                }
                teacher_classes.append(class_info)
        teacher_info['classes'] = teacher_classes"""

        # Get all the units for this instructor
        unit_query = DataStoreManager(key_id=DatastoreKeyTypes.UNIT.value).query()
        unit_query.add_filter('instructor_id', '=', teacher_email)
        unit_list = list(unit_query.fetch())
        # Sort queried units into active and expired
        active_units = []
        expired_units = []
        teacher_classes = []
        if unit_list:
            for unit in unit_list:
                if 'name' in unit['summary']:
                    if 'expires' in unit['workspace_settings']:
                        creation_ts = unit['creation_timestamp']
                        expire_ts = unit['workspace_settings']['expires']
                        unit_info = {
                            'id': unit.key.name,
                            'name': unit['summary']['name'],
                            'created': creation_ts,
                            'expires': expire_ts,
                            'build_count': unit['workspace_settings']['count']
                        }
                        if (int(time.time()) - (int(creation_ts) + (int(expire_ts) * 60 * 60 * 24))) < 0:
                            active_units.append(unit_info)
                        else:
                            expired_units.append(unit_info)
                    else:
                        unit_info = {
                            'unit_id': unit.key.name,
                            'name': unit['summary']['name'],
                            'description': unit['summary']['description'],
                            'created':  unit['creation_timestamp'],
                            'build_count': unit['workspace_settings']['count']
                        }
                        expired_units.append(unit_info)
            teacher_info['active_units'] = sorted(active_units, key=lambda i: (i['created']), reverse=True)
            teacher_info['expired_units'] = sorted(expired_units, key=lambda i: (i['timestamp']), reverse=True)
        # Get list of workouts from cloud bucket
        # TODO: Consider preloading all specs into a cyberarena-catalog entity
        workout_specs = {
            'assignments': BucketManager().get_workouts(),
            'live': [],
            'escape_rooms': []
        }
        return render_template('teacher_classroom.html', auth_config=auth_config, auth_list=auth_list,
                               teacher_info=teacher_info, workout_specs=workout_specs)
    else:
        return redirect('/login')


@teacher_app.route('/class/<class_id>', methods=['GET', 'POST'])
def teacher_class(class_id):
    if session.get('user_email', None):
        teacher_email = session['user_email']
        teacher_info = DataStoreManager(key_type=DatastoreKeyTypes.INSTRUCTOR, key_id=str(teacher_email)).get()
        class_instance = DataStoreManager(key_type=DatastoreKeyTypes.CLASSROOM, key_id=str(class_id)).get()
        if class_instance:
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
                    'id': class_instance['class_id'],
                    'name': class_instance['class_name'],
                    'roster': sorted_roster,
                    'student_auth': class_instance['student_auth'] if 'student_auth' in class_instance else 'anonymous',
                    'class_units': class_unit_list
                }
            teacher_info['class_info'] = class_info

            # Get all the units current instructor class
            unit_query = DataStoreManager(key_id=DatastoreKeyTypes.UNIT.value).query()
            unit_query.add_filter('id', '=', 'class_name')
            unit_list = list(unit_query.fetch())

            # Sort queried units into active and expired
            active_units = []
            expired_units = []
            teacher_classes = []
            if unit_list:
                for unit in unit_list:
                    summary = unit['summary']
                    if 'workout_name' in unit:
                        if 'expiration' in unit:
                            creation_ts = unit['creation_timestamp']
                            expire_ts = unit['workspace_settings']['expires']
                            unit_info = {
                                'unit_id': unit.key.name,
                                'name': unit['summary']['name'],
                                'description': unit['summary']['description'],
                                'timestamp': creation_ts,
                                'expires': expire_ts,
                            }
                            if (int(time.time()) - (int(creation_ts) + (int(expire_ts) * 60 * 60 * 24))) < 0:
                                active_units.append(unit_info)
                            else:
                                expired_units.append(unit_info)
                        else:
                            unit_info = {
                                'unit_id': unit.key.name,
                                'name': unit['summary']['name'],
                                'description': unit['summary']['description'],
                                'timestamp':  unit['creation_timestamp'],
                            }
                            expired_units.append(unit_info)
                teacher_info['active_units'] = sorted(active_units, key=lambda i: (i['timestamp']), reverse=True)
                teacher_info['expired_units'] = sorted(expired_units, key=lambda i: (i['timestamp']), reverse=True)
            workout_specs = BucketManager().get_workouts()
            return render_template('teacher_classroom.html', auth_config=auth_config, teacher_info=teacher_info,
                                   workout_specs=workout_specs)
    abort(404)


@teacher_app.route('/build/<workout_type>', methods=['GET'])
def build(workout_type):
    logger.info('Request for workout type %s' % workout_type)
    form = CreateWorkoutForm()
    return render_template('build_workout.html', workout_type=workout_type, auth_config=auth_config)


# Instructor landing page. Displays information and links for a unit of workouts
@teacher_app.route('/workout_list/<unit_id>', methods=['GET', 'POST'])
def workout_list(unit_id):
    ds_manager = DataStoreManager(key_type=DatastoreKeyTypes.UNIT, key_id=str(unit_id))
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
                               attack_spec=attack_yaml, auth_config=auth_config)
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
