import json
import time
from datetime import datetime, timezone
from flask import abort, Blueprint, jsonify, redirect, render_template, request, session, url_for
from main_app_utilities.gcp.arena_authorizer import ArenaAuthorizer
from main_app_utilities.gcp.cloud_env import CloudEnv
from main_app_utilities.gcp.datastore_manager import DataStoreManager
from main_app_utilities.globals import DatastoreKeyTypes, get_current_timestamp_utc, WorkoutStates

student_app = Blueprint('student_app', __name__, url_prefix="/student",
                        static_folder="./static",
                        template_folder="./templates")
cloud_env = CloudEnv()


@student_app.route('/join/', methods=['GET'])
def claim_workout():
    api_route = url_for('workout')
    error = request.args.get('error', None)
    if not error:
        return render_template('claim_workout.html', api=api_route)
    else:
        if error == '404':
            error_msg = 'Invalid Join Code'
        elif error == '406':
            error_msg = 'No workouts available! Contact your instructor for further direction'
        else:
            error_msg = 'Something went wrong ...'
    return render_template('claim_workout.html', api=api_route, error=error_msg)


@student_app.route('/escape-room/join/', methods=['GET'])
def claim_escape_room():
    api_route = url_for('team')
    error = request.args.get('error', None)
    parent = request.args.get('parent', None)
    if parent:
        # EscapeRoom team list view
        workout_list = DataStoreManager().get_children(child_key_type=DatastoreKeyTypes.WORKOUT,
                                                       parent_id=parent)
        if workout_list:
            escape_rooms = [{'id': i['id'], 'team_name': i['team_name']} for i in workout_list]
            return render_template('claim_escape_room.html', api=api_route, escape_rooms=escape_rooms)
        return render_template('claim_escape_room.html', api=api_route, error='Invalid Join Code')
    elif error:
        # Error View
        if error == '404':
            error_msg = 'Invalid Join Code'
        elif error == '406':
            error_msg = 'No Escape Room available! Contact your instructor for further direction'
        else:
            error_msg = 'Something went wrong ...'
        return render_template('claim_escape_room.html', api=api_route, error=error_msg)
    else:
        # Base view
        return render_template('claim_escape_room.html', api=api_route)


@student_app.route('/home', methods=['GET', 'POST'])
def registered_student_home():
    if 'user_email' in session and 'user_groups' in session:
        student_email = session['user_email']
        if ArenaAuthorizer.UserGroups.STUDENTS.value not in session['user_groups']:
            return redirect('/403')

        workout_list = DataStoreManager().get_workouts(student_email=student_email)
        student_workouts = []
        for workout in workout_list:
            if workout['state'] != 'DELETED':
                workout_info = {
                    'workout_id': workout.key.name,
                    'workout_name': workout['type'],
                    'timestamp': workout['timestamp']
                }
                student_workouts.append(workout_info)
        student_workouts = sorted(student_workouts, key=lambda i: (i['timestamp']), reverse=True)

        student_info = {'workouts': student_workouts}
        return render_template('student_home.html', auth_config=cloud_env.auth_config, student_info=student_info)
    else:
        return redirect('/login')


@student_app.route('/assignment/workout/<build_id>', methods=['GET'])
def workout_view(build_id):
    auth_config = cloud_env.auth_config
    workout_info = DataStoreManager(key_type=DatastoreKeyTypes.WORKOUT.value, key_id=build_id).get()
    if workout_info:
        parent_id = workout_info.get('parent_id', None)
        if workout_info and parent_id:
            unit = DataStoreManager(key_type=DatastoreKeyTypes.UNIT.value, key_id=parent_id).get()
            server_list = DataStoreManager().get_children(child_key_type=DatastoreKeyTypes.SERVER.value, parent_id=build_id)
            if unit:
                workout_info['summary'] = unit['summary']
                workout_info['expires'] = unit['workspace_settings']['expires']
                current_ts = get_current_timestamp_utc()
                is_expired = True
                if current_ts <= workout_info['expires']:
                    workout_info['expired'] = is_expired = False

                # TODO: Need to check to see if workout is already running; If yes, get expected stop ts
                if not is_expired:
                    # If shutoff_timestamp exists, then the workout is running
                    if workout_info.get('shutoff_timestamp', None):
                        workout_info['remaining_time'] = workout_info['shutoff_timestamp'] - current_ts
                else:
                    workout_info['remaining_time'] = -9999

            # If they exist, get the entry point information for each server
            connections = _generate_connection_urls(workout_info)
            if workout_info.get('servers', None):
                for server in workout_info['servers']:
                    entry_point = server.get('human_interaction', None)
                    if entry_point:
                        server['url'] = connections['server'].get(server['name'], None)
            workout_info['api'] = {'workout': url_for('workout'),}
            return render_template('student_workout.html', auth_config=auth_config, workout=workout_info,
                                   server_list=server_list, project_id=cloud_env.project)
    return redirect(url_for('student_app.claim_workout', error=500))


@student_app.route('/escape-room/team/<build_id>', methods=['GET'])
def escape_room(build_id):
    auth_config = cloud_env.auth_config
    workout = DataStoreManager(key_type=DatastoreKeyTypes.WORKOUT, key_id=build_id).get()
    if workout:
        unit = DataStoreManager(key_type=DatastoreKeyTypes.UNIT, key_id=workout['parent_id']).get()
        if workout['escape_room'].get('start_time', None) and workout.get('state', None) == WorkoutStates.RUNNING.value:
            start_time = workout['escape_room']['start_time']
            time_limit = workout['escape_room']['time_limit']
            current_time = get_current_timestamp_utc()
            time_remaining = time_limit - (current_time - start_time)
            if time_remaining > 0:
                workout['escape_room']['expired'] = False
                workout['escape_room']['time_remaining'] = time_remaining
            else:
                workout['escape_room']['expired'] = True
                workout['escape_room']['time_remaining'] = 0
            # Calculate how many puzzles have been solved
            workout['escape_room']['number_correct'] = sum(1 for i in workout['escape_room']['puzzles'] if i['correct'])
            # Get the connection urls for vms and web applications
            workout['links'] = _generate_connection_urls(workout)
            workout['links']['student_instructions_url'] = unit['summary']['student_instructions_url']
            return render_template('student_escape_room.html', workout=workout, auth_config=auth_config)
        else:  # the escape room hasn't been started yet, return waiting room template
            workout['expires'] = unit['workspace_settings'].get('expires', None)
            if workout['expires'] < get_current_timestamp_utc():
                workout['expired'] = True
            return render_template('student_escape_room_waiting.html', auth_config=auth_config, workout=workout)
    abort(404)


@student_app.route('/fixed-arena/class/<build_id>/signup', methods=['GET', 'POST'])
def fixed_arena_signup(build_id):
    if request.method == 'POST':
        recv_data = request.form
        print(recv_data)
        student_name = recv_data.get('student_name', None)
        if not student_name:
            abort(400)
        # Query the workspaces for the current class
        workspace_query = DataStoreManager(key_id=DatastoreKeyTypes.FIXED_ARENA_WORKSPACE.value).query(
            filter_key='parent_id', op='=', value=build_id)

        # Check for unclaimed workspace
        claimed_workspace = None
        for workspace in workspace_query:
            if 'student_name' in workspace:
                if workspace['student_name'] == None or workspace['student_name'] == "":
                    claimed_workspace = workspace
                    claimed_workspace['student_name'] = student_name
                    DataStoreManager(key_type=DatastoreKeyTypes.FIXED_ARENA_WORKSPACE.value,
                                     key_id=claimed_workspace.key.name).put(obj=claimed_workspace)
                    return redirect('/student/fixed-arena/%s' % claimed_workspace.key.name)
            else:
                claimed_workspace = workspace
                claimed_workspace['student_name'] = student_name
                DataStoreManager(key_type=DatastoreKeyTypes.FIXED_ARENA_WORKSPACE.value,
                                 key_id=claimed_workspace.key.name).put(obj=claimed_workspace)
                return redirect('/student/fixed-arena/%s' % claimed_workspace.key.name)
        return render_template('student_signup.html', class_full=True)
    else:
        return render_template('student_signup.html')


@student_app.route('/fixed-arena/<build_id>', methods=['GET'])
def fixed_arena_student(build_id):
    auth_config = cloud_env.auth_config
    fixed_arena_workout = DataStoreManager(key_type=DatastoreKeyTypes.FIXED_ARENA_WORKSPACE.value,
                                           key_id=build_id).get(wait=True)
    parent_id = fixed_arena_workout.get('parent_id', None)
    fixed_arena_class = DataStoreManager(key_type=DatastoreKeyTypes.FIXED_ARENA_CLASS.value, key_id=parent_id).get()
    registration_required = fixed_arena_class['workspace_settings'].get('registration_required', False)
    logged_in_user = session.get('user_email', None)
    workspace_servers = DataStoreManager(key_id=DatastoreKeyTypes.SERVER.value).query(filter_key='parent_id',
                                                                                      op='=', value=build_id)
    server_list = []
    if fixed_arena_class:
        expiration = fixed_arena_class['workspace_settings'].get('expires', None)
        is_expired = True
        ts = datetime.now(timezone.utc).replace(tzinfo=timezone.utc).timestamp()
        if ts <= expiration:
            is_expired = False
        dns_suffix = cloud_env.dns_suffix

        # Get entry point from fixed_arena_class
        entry_point = None
        expiration_iso8601 = datetime.fromtimestamp(expiration).replace(microsecond=0)
        for server in fixed_arena_workout['servers']:
            entry_point = server.get('human_interaction', None)[0]
            server_ip = server.get('nics', None)[0]
            server_name = server.get('name', None)
            if entry_point:
                entry_server = {
                    'entry_point': entry_point,
                    'ip': server_ip,
                    'name': server_name
                }
                break
        """
        TODO: Clean up objects above to return this instead:
        return render_template('fixed_arena_student.html', fixed_arena_class=fixed_arena_class, 
                               fixed_arena_workout=fixed_arena_workout, dns_suffix=dns_suffix, 
                               expiration_iso8601=expiration_iso8601)"""
        return render_template('fixed_arena_student.html', fixed_arena_class=fixed_arena_class, fixed_arena_workout=fixed_arena_workout, dns_suffix=dns_suffix,
                               expiration=expiration, is_expired=is_expired, auth_config=auth_config, serverip=server_ip, servername=server_name,
                               servers=workspace_servers, entry_point=entry_point, expiration_iso8601=expiration_iso8601, entry_server=entry_server)
    else:
        return redirect('/no-workout')


def _generate_connection_urls(workout_info):
    """
       :param workout_info: dictionary object holding all the workout information
       :return: dict(server: dict(), web_applications: dict()) if exists
       """
    dns_suffix = cloud_env.dns_suffix
    build_id = workout_info['id']
    links = {'server': dict(), 'web_application': dict()}
    if workout_info.get('proxy_connections', None):
        for conn in workout_info['proxy_connections']:
            username = conn['username']
            password = conn['password']
            # Build the guacamole connection url with generated username and password
            url = f"http://{build_id}-display{dns_suffix}:8080/guacamole/#/?username={username}&password={password}"
            links['server'][conn['server']] = url
    if workout_info.get('web_applications', None):
        for app in workout_info['web_applications']:
            links['web_application'][app['name']] = app['url']
    return links


# [ eof ]
