import logging as logger
import json
import time
from flask import abort, Blueprint, redirect, render_template, request, session, url_for

from main_app_utilities.gcp.arena_authorizer import ArenaAuthorizer
from main_app_utilities.gcp.cloud_env import CloudEnv
from main_app_utilities.gcp.datastore_manager import DataStoreManager
from main_app_utilities.globals import DatastoreKeyTypes, BuildConstants, get_current_timestamp_utc

teacher_app = Blueprint('teacher_app', __name__, url_prefix="/teacher",
                        static_folder="./static", template_folder="./templates")
cloud_env = CloudEnv()


@teacher_app.route('/home', methods=['GET', 'POST'])
def teacher_home():
    if session.get('user_email', None):
        teacher_email = session['user_email']
        auth = ArenaAuthorizer(env_dict=cloud_env.get_env())
        auth_list = auth.get_user_groups(user=teacher_email)  # Get user auth levels
        teacher_info = {}

        # Get all the units for this instructor
        unit_query = DataStoreManager(key_id=DatastoreKeyTypes.UNIT.value).query()
        unit_query.add_filter('instructor_id', '=', teacher_email)
        unit_list = list(unit_query.fetch())
        # Sort queried units into active and expired
        active_units = []
        expired_units = []
        if unit_list:
            for unit in unit_list:
                if 'name' in unit['summary']:
                    if 'expires' in unit['workspace_settings']:
                        creation_ts = unit['creation_timestamp']
                        expire_ts = unit['workspace_settings']['expires']
                        unit_info = {
                            'id': unit.key.name,
                            'name': unit['summary']['name'],
                            'description': unit['summary']['description'],
                            'created': creation_ts,
                            'expires': expire_ts,
                            'build_count': unit['workspace_settings']['count'],
                            'build_type': unit['build_type']
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
                            'build_count': unit['workspace_settings']['count'],
                            'build_type': unit['build_type']
                        }
                        expired_units.append(unit_info)
            teacher_info['active_units'] = sorted(active_units, key=lambda i: (i['created']), reverse=True)
            teacher_info['expired_units'] = sorted(expired_units, key=lambda i: (i['timestamp']), reverse=True)

        # Get list of workouts from datastore catalog
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
        # Get api urls
        urls = _get_api_urls(return_all=True)
        return render_template('teacher_classroom.html', auth_config=cloud_env.auth_config, auth_list=auth_list,
                               teacher_info=teacher_info, workout_specs=workout_specs, urls=urls)
    else:
        return redirect('/login')


# Instructor unit page. Displays information and links for a unit of workouts
@teacher_app.route('/assignment/<unit_id>', methods=['GET'])
def workout_list(unit_id):
    auth = ArenaAuthorizer(env_dict=cloud_env.get_env())
    if session.get('user_email', None):
        teacher_email = session['user_email']
        auth_list = auth.get_user_groups(teacher_email)

        # Get assignment data
        unit = DataStoreManager(key_type=DatastoreKeyTypes.UNIT, key_id=str(unit_id)).get()
        if unit:
            join_url = ''
            if unit.get('join_code', None):
                join_url = f"{request.host_url.rstrip('/')}{url_for('student_app.claim_workout')}"
            workouts_list = DataStoreManager().get_children(child_key_type=DatastoreKeyTypes.WORKOUT, parent_id=unit_id)
            attack_specs = list(DataStoreManager(key_id=DatastoreKeyTypes.CYBERARENA_ATTACK_SPEC).query().fetch())
            if len(workouts_list) > 0:
                registration_required = unit.get('registration_required', False)
                unit['api'] = _get_api_urls(build_type=unit['build_type'])

                # Check if Unit is expired
                current_ts = get_current_timestamp_utc()
                is_expired = True
                if current_ts <= unit['workspace_settings']['expires']:
                    is_expired = False
                unit['expired'] = is_expired
                unit['human_interaction'] = {'servers': False, 'web_applications': False}

                if workouts_list[0].get('servers', False):
                    unit['human_interaction']['servers'] = True
                if workouts_list[0].get('web_applications', False):
                    unit['human_interaction']['web_applications'] = True
                return render_template('workout_list.html', auth_config=cloud_env.auth_config, auth_list=auth_list,
                                       workout_list=workouts_list, unit=unit, join_url=join_url,
                                       attack_specs=attack_specs)
            return render_template('workout_list.html', auth_config=cloud_env.auth_config, auth_list=auth_list,
                                   workout_list=False, unit=unit, join_url=join_url,
                                   attack_specs=attack_specs)
        return redirect('/no-workout')
    return redirect('/login')


@teacher_app.route('/escape-room/<unit_id>', methods=['GET'])
def escape_room(unit_id):
    auth = ArenaAuthorizer(env_dict=cloud_env.get_env())
    if session.get('user_email', None):
        teacher_email = session['user_email']
        auth_list = auth.get_user_groups(teacher_email)
        unit = dict(DataStoreManager(key_type=DatastoreKeyTypes.UNIT, key_id=str(unit_id)).get())
        if unit:
            unit['escape_room']['time_remaining'] = 0
            workouts_list = DataStoreManager().get_children(child_key_type=DatastoreKeyTypes.WORKOUT, parent_id=unit_id)
            join_url = ''
            if unit.get('join_code', None):
                join_url = f"{request.host_url.rstrip('/')}{url_for('student_app.claim_escape_room')}"
            if len(workouts_list) > 0:
                unit['api'] = _get_api_urls(build_type=unit['build_type'])

                # Check if Unit is expired
                current_ts = get_current_timestamp_utc()
                is_expired = True
                if current_ts <= unit['workspace_settings']['expires']:
                    is_expired = False
                unit['expired'] = is_expired

                # Check to see if the Escape Room has any servers or web_applications
                # This is a way to bypass Jinja templating errors for keys
                unit['human_interaction'] = {'servers': False, 'web_applications': False}
                for workout in workouts_list:
                    if workout.get('servers', False):
                        unit['human_interaction']['servers'] = True
                    if workout.get('web_application', False):
                        unit['human_interaction']['web_applications'] = True
                    # Check the Escape Room timer to see if it is still valid
                    unit['escape_room']['expired'] = workout['escape_room'].get('expired', False)
                    start_time = workout['escape_room']['start_time']
                    time_limit = workout['escape_room']['time_limit']
                    current_time = get_current_timestamp_utc()
                    time_remaining = time_limit - (current_time - start_time)
                    # We assume if start_time == 0, the escape room hasn't been started yet
                    if time_remaining > 0 or start_time == 0:
                        unit['escape_room']['expired'] = False
                        unit['escape_room']['time_remaining'] = time_remaining
                    else:  # Escape Room timer has expired
                        unit['escape_room']['expired'] = True
                    unit['escape_room']['time_remaining'] = time_remaining
                    break
                return render_template('teacher_escape_room.html', auth_config=cloud_env.auth_config, auth_list=auth_list,
                                       unit=dict(unit), workout_list=list(workouts_list), join_url=join_url)
            return render_template('teacher_escape_room.html', auth_config=cloud_env.auth_config, auth_list=auth_list,
                                   unit=dict(unit), workout_list=[], join_url=join_url)
        return redirect('/no-workout')
    return redirect('/login')


def _get_api_urls(build_type=None, return_all=False):
    urls = {
        'unit': url_for('unit'),
        'escape_room': url_for('escape-room'),
        'fixed_arena': url_for('fixed-arena'),
        'fixed_arena_class': url_for('class'),
    }
    if not return_all:
        return urls.get(build_type)
    return urls
# [ eof ]
