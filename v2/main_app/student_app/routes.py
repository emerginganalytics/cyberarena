import json
import time
from datetime import datetime, timezone
from flask import abort, Blueprint, jsonify, redirect, render_template, request, session, url_for
from main_app_utilities.gcp.arena_authorizer import ArenaAuthorizer
from main_app_utilities.gcp.cloud_env import CloudEnv
from main_app_utilities.gcp.compute_manager import ComputeManager
from main_app_utilities.gcp.datastore_manager import DataStoreManager
from main_app_utilities.globals import DatastoreKeyTypes, get_current_timestamp_utc

student_app = Blueprint('student_app', __name__, url_prefix="/student",
                        static_folder="./static",
                        template_folder="./templates")


@student_app.route('/home', methods=['GET', 'POST'])
def registered_student_home():
    if 'user_email' in session and 'user_groups' in session:
        student_email = session['user_email']
        if ArenaAuthorizer.UserGroups.STUDENTS not in session['user_groups']:
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
        return render_template('student_home.html', auth_config=CloudEnv().auth_config, student_info=student_info)
    else:
        return redirect('/login')


@student_app.route('/landing/<workout_id>', methods=['GET', 'POST'])
def landing_page(workout_id):
    dns_suffix = CloudEnv().dns_suffix
    auth_config = CloudEnv().auth_config
    unit_list = DataStoreManager(key_id=DatastoreKeyTypes.CYBERGYM_UNIT).query()
    workouts_list = list(unit_list.add_filter('workouts', '=', str(workout_id)).fetch())
    if not workouts_list:
        return redirect('/404')
    else:
        workout = DataStoreManager(key_type=DatastoreKeyTypes.CYBERGYM_WORKOUT.value, key_id=workout_id).get()
        unit = DataStoreManager(key_type=DatastoreKeyTypes.CYBERGYM_UNIT.value, key_id=workout['unit_id']).get()
        admin_info = DataStoreManager(key_type=DatastoreKeyTypes.ADMIN_INFO.value, key_id='cybergym').get()

    registration_required = workout.get('registration_required', False)
    logged_in_user = session.get('user_email', None)
    registered_user = workout.get('student_email', None)
    instructor_user = unit.get('instructor_id', None)
    allowed_users = admin_info['admins'].copy() + [instructor_user] + [registered_user]
    workout_server_query = DataStoreManager(key_id=workout_id).get_servers()

    server_list = []
    for server in workout_server_query:
        server_name = server['name'][11:]
        server['name'] = server_name
        snapshots_list = ComputeManager(key_id=server.key.name).get_snapshots()
        snapshots = snapshots_list.get('snapshots', None)
        if snapshots:
            server['snapshots'] = []
            for snapshot in snapshots['items']:
                server['snapshots'].append({'snapshot_name': snapshot['name'], 'creation_date': snapshot['creationTimestamp']})
        server_list.append(server)
    if registration_required and logged_in_user not in allowed_users:
        return render_template('login.html', auth_config=auth_config)

    if workout:
        # TODO: AssessmentManager Needs to be updated to match current direction
        # assessment_manager = CyberArenaAssessment(workout_id)
        expiration = None
        is_expired = True
        if 'expiration' in workout:
            if (int(time.time()) - (int(workout['timestamp']) + ((int(workout['expiration'])) * 60 * 60 * 24))) < 0:
                is_expired = False
            expiration = time.strftime('%d %B %Y', (
                time.localtime((int(workout['expiration']) * 60 * 60 * 24) + int(workout['timestamp']))))
        shutoff = None
        if 'run_hours' in workout:
            run_hours = int(workout['run_hours'])
            if run_hours == 0:
                shutoff = "expired"
            else:
                shutoff = time.strftime('%d %B %Y at %I:%M %p',
                                        (time.localtime((int(workout['run_hours']) * 60 * 60) + int(workout['start_time']))))
        build_type = unit['build_type']
        container_url = None
        if build_type == 'container':
            container_url = workout['container_url']

        assessment = None
        # TODO: AssessmentManager Needs to be updated to match current direction
        # if 'assessment' in workout and workout['assessment']:
        #    assessment = assessment_manager.get_assessment_questions()
        build_now = unit.get('build_now', True)
        # if request.method == "POST":
        #    attempt = assessment_manager.submit()
        #    return json.dumps(attempt)
        return render_template('landing_page.html', build_type=build_type, workout=workout,
                               description=unit['description'], container_url=container_url,
                               dns_suffix=dns_suffix, expiration=expiration,
                               shutoff=shutoff, assessment=assessment, is_expired=is_expired,
                               build_now=build_now, auth_config=auth_config,
                               servers=server_list)
    else:
        return redirect('/no-workout')


@student_app.route('/<unit_id>/signup', methods=['GET', 'POST'])
def unit_signup(unit_id):
    unit = DataStoreManager(key_type=DatastoreKeyTypes.CYBERGYM_UNIT.value, key_id=unit_id).get()
    if request.method == 'POST':
        workout_query = DataStoreManager(key_id=DatastoreKeyTypes.CYBERGYM_WORKOUT).query()
        workout_query.add_filter('unit_id', '=', unit_id)
        workout_list = list(workout_query.fetch())
        claimed_workout = None
        for workout in workout_list:
            if 'student_name' in workout:
                if workout['student_name'] == None or workout['student_name'] == "":
                    claimed_workout = workout
                    claimed_workout['student_name'] = request.form['student_name']
                    DataStoreManager(key_id=DatastoreKeyTypes.FIXED_ARENA_WORKSPACE.value).put(obj=claimed_workout)
                    if unit['build_type'] == 'arena':
                        return redirect('/student/arena_landing/%s' % claimed_workout.key.name)
                    else:
                        return redirect('/student/landing/%s' % claimed_workout.key.name)
            else:
                claimed_workout = workout
                claimed_workout['student_name'] = request.form['student_name']
                DataStoreManager(key_id=DatastoreKeyTypes.FIXED_ARENA_WORKSPACE.value).put(obj=claimed_workout)
                if unit['build_type'] == 'arena':
                    return redirect('/student/arena_landing/%s' % claimed_workout.key.name)
                else:
                    return redirect('/student/landing/%s' % claimed_workout.key.name)
        return render_template('unit_signup.html', unit_full=True)
    return render_template('unit_signup.html')


# TODO: Will replace student_app.landing_page route
@student_app.route('/assignment/workout/<build_id>', methods=['GET'])
def workout_view(build_id):
    auth_config = CloudEnv().auth_config
    workout_info = DataStoreManager(key_type=DatastoreKeyTypes.WORKOUT.value, key_id=build_id).get()
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
                workout_info['remaining_time'] = workout_info['expires'] - current_ts
                """ TODO: Need to establish a method to handle start times; i.e. what is the default run time for a workout?
                    Will we allow students to set an arbitrary run time when starting the workout? Or do  we want to have a default
                    runtime that will be used
                """
                if not workout_info.get('start_time', None):
                    workout_info['start_time'] = 0
                if not workout_info.get('time_limit', 0):
                    workout_info['time_limit'] = 0
            else:
                workout_info['remaining_time'] = 0

        # If they exist, get the entry point information for each server
        connections = _generate_connection_urls(workout_info)
        if workout_info.get('servers', None):
            for server in workout_info['servers']:
                entry_point = server.get('human_interaction', None)
                if entry_point:
                    server['url'] = connections['server'][server['name']]
        workout_info['api'] = {'workout': url_for('workout'),}
        return render_template('student_workout.html', auth_config=auth_config, workout=workout_info,
                               server_list=server_list)
    return redirect('/no-workout')


@student_app.route('/escape-room/team/<build_id>', methods=['GET'])
def escape_room(build_id):
    auth_config = CloudEnv().auth_config
    workout = DataStoreManager(key_type=DatastoreKeyTypes.WORKOUT, key_id=build_id).get()
    if workout:
        unit = DataStoreManager(key_type=DatastoreKeyTypes.UNIT, key_id=workout['parent_id']).get()
        if workout['escape_room'].get('start_time', None):
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
            workout['escape_room']['number_correct'] = sum(1 for i in workout['escape_room']['puzzles'] if i['correct'])
            workout['links'] = _generate_connection_urls(workout)
            workout['links']['instructions_url'] = unit['summary']['student_instructions_url']
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
    auth_config = CloudEnv().auth_config
    fixed_arena_workout = DataStoreManager(key_type=DatastoreKeyTypes.FIXED_ARENA_WORKSPACE.value, key_id=build_id).get()
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
        dns_suffix = CloudEnv().dns_suffix

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
    dns_suffix = CloudEnv().dns_suffix
    build_id = workout_info['id']
    links = {'server': dict(), 'web_application': dict()}
    if workout_info.get('proxy_connections', None):
        for conn in workout_info['proxy_connections']:
            username = conn['username']
            password = conn['password']
            url = f"http://{build_id}-display{dns_suffix}:8080/guacamole/#/?username={username}&password={password}"
            links['server'][conn['server']] = url
    if workout_info.get('web_applications', None):
        for app in workout_info['web_applications']:
            links['web_application'][app['name']] = app['url']
    return links

# [ eof ]
