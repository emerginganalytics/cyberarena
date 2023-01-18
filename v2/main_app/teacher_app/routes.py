import logging as logger
import json
import time

import flask.app
from flask import abort, Blueprint, redirect, render_template, request, session, url_for
from forms.forms import CreateWorkoutForm
from main_app_utilities.gcp.arena_authorizer import ArenaAuthorizer
from main_app_utilities.gcp.bucket_manager import BucketManager
from main_app_utilities.gcp.cloud_env import CloudEnv
from main_app_utilities.gcp.datastore_manager import DataStoreManager
from main_app_utilities.globals import DatastoreKeyTypes, BuildConstants

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
        specs = list(DataStoreManager(key_id=DatastoreKeyTypes.CATALOG.value).query().fetch())
        workout_specs = {
            'assignments': [],
            'live': [],
            'escape_rooms': [],
        }
        for spec in specs:
            build_type = spec['build_type']
            if build_type == BuildConstants.BuildType.UNIT.value:
                workout_specs['assignments'].append(spec)
            elif build_type in BuildConstants.BuildType.FIXED_ARENA.value:
                workout_specs['live'].append(spec)
            elif build_type == BuildConstants.BuildType.ESCAPE_ROOM.value:
                workout_specs['escape_rooms'].append(spec)
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
            workout_specs = list(DataStoreManager(key_id=DatastoreKeyTypes.CATALOG).query())
            return render_template('teacher_classroom.html', auth_config=auth_config, teacher_info=teacher_info,
                                   workout_specs=workout_specs)
    abort(404)


@teacher_app.route('/build/<workout_type>', methods=['GET'])
def build(workout_type):
    urls = {
        'unit': url_for('unit'),
        'escape_room': url_for('escape-room'),
        'fixed_arena': url_for('fixed-arena'),
        'fixed_arena_class': url_for('class'),
    }
    spec = DataStoreManager(key_type=DatastoreKeyTypes.CATALOG, key_id=workout_type).get()
    if spec:
        spec['api'] = urls[spec['build_type']]
        return render_template('build_workout.html', spec=spec, workout_type=workout_type, auth_config=auth_config)
    abort(404)


# Instructor landing page. Displays information and links for a unit of workouts
@teacher_app.route('/assignment/<unit_id>', methods=['GET'])
def workout_list(unit_id):
    auth = ArenaAuthorizer()
    if session.get('user_email', None):
        teacher_email = session['user_email']
        auth_list = auth.get_user_groups(teacher_email)

        # Get assignment data
        unit = DataStoreManager(key_type=DatastoreKeyTypes.UNIT, key_id=str(unit_id)).get()
        build_type = unit['build_type']
        attack_specs = list(DataStoreManager(key_id=DatastoreKeyTypes.CYBERARENA_ATTACK_SPEC).query().fetch())
        workout_list = DataStoreManager().get_children(child_key_type=DatastoreKeyTypes.WORKOUT, parent_id=unit_id)
        if unit and len(str(workout_list)) > 0:
            registration_required = unit.get('registration_required', False)
            if not registration_required:
                workout_list = sorted(workout_list, key=lambda i: (i['student_name']))
            else:
                workout_list = sorted(workout_list, key=lambda i: (i['student_name']['student_name']))
            return render_template('workout_list.html', auth_config=auth_config, auth_list=auth_list,
                                   workout_list=workout_list, unit=unit, main_app_url=CloudEnv().main_app_url,
                                   attack_specs=attack_specs)
        return redirect('/no-workout')
    return redirect('/login')

# [ eof ]
