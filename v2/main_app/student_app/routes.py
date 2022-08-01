import json
import time
from flask import Blueprint, jsonify, redirect, render_template, request, session
from utilities.gcp.arena_authorizer import ArenaAuthorizer
from utilities.gcp.cloud_env import CloudEnv
from utilities.gcp.compute_manager import ComputeManager
from utilities.gcp.datastore_manager import DataStoreManager
from utilities.globals import DatastoreKeyTypes

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
                               servers=server_list, survey=survey)
    else:
        return redirect('/no-workout')


@student_app.route('/arena_landing/<workout_id>', methods=['GET', 'POST'])
def arena_landing(workout_id):
    dns_suffix = CloudEnv().dns_suffix
    workout = DataStoreManager(key_type=DatastoreKeyTypes.CYBERGYM_WORKOUT.value, key_id=workout_id).get()
    unit = DataStoreManager(key_type=DatastoreKeyTypes.CYBERGYM_UNIT.value, key_id=workout['unit_id']).get()

    # TODO: Possibly need to rework this functionality
    arena_server_info = [] # get_arena_ip_addresses_for_workout(workout_id)
    # TODO: CyberArenaAssessment needs to be updated to match current direction
    # assessment_manager = CyberArenaAssessment(workout_id)
    student_instructions_url = None
    if 'student_instructions_url' in workout:
        student_instructions_url = workout['student_instructions_url']
    formatted_instruction_url = student_instructions_url
    assessment = guac_user = guac_pass = flags_found = None

    if 'workout_user' in workout:
        guac_user = workout['workout_user']
    if 'workout_password' in workout:
        guac_pass = workout['workout_password']
    return render_template('arena_landing.html', description=unit['description'], unit_id=unit.key.name,
                           assessment=assessment, workout=workout, dns_suffix=dns_suffix,
                           guac_user=guac_user, guac_pass=guac_pass, arena_id=workout_id,
                           student_instructions=formatted_instruction_url, server_info=arena_server_info)


@student_app.route('/feedback/<workout_id>', methods=['POST'])
def student_feedback(workout_id):
    if request.method == 'POST':
        data = request.form
        # store_student_feedback(data, workout_id)
        return json.dumps(data)


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
                    DataStoreManager().put(obj=claimed_workout)
                    if unit['build_type'] == 'arena':
                        return redirect('/student/arena_landing/%s' % claimed_workout.key.name)
                    else:
                        return redirect('/student/landing/%s' % claimed_workout.key.name)
            else:
                claimed_workout = workout
                claimed_workout['student_name'] = request.form['student_name']
                DataStoreManager().put(obj=claimed_workout)
                if unit['build_type'] == 'arena':
                    return redirect('/student/arena_landing/%s' % claimed_workout.key.name)
                else:
                    return redirect('/student/landing/%s' % claimed_workout.key.name)
        return render_template('unit_signup.html', unit_full=True)
    return render_template('unit_signup.html')

@student_app.route('/fixed-arena-landing/<workout_id>', methods=['GET', 'POST'])
def fixed_arena_landing_page(workout_id):
    unit_list = ds_client.query(kind='cybergym-unit')
    workouts_list = list(unit_list.add_filter('workouts', '=', str(workout_id)).fetch())
    if not workouts_list:
        return redirect('/404')
    else:
        workout = ds_client.get(ds_client.key('cybergym-workout', workout_id))
        unit = ds_client.get(ds_client.key('cybergym-unit', workout['unit_id']))
        admin_info = ds_client.get(ds_client.key('cybergym-admin-info', 'cybergym'))

    registration_required = workout.get('registration_required', False)
    logged_in_user = session.get('user_email', None)
    registered_user = workout.get('student_email', None)
    instructor_user = unit.get('instructor_id', None)
    allowed_users = admin_info['admins'].copy() + [instructor_user] + [registered_user]
    workout_server_query = ds_client.query(kind='cybergym-server')
    workout_server_query.add_filter('workout', '=', workout_id)
    server_list = []
    survey_yaml = YamlFunctions().parse_yaml(yaml_filename='survey')
    survey = survey_yaml.get('survey', None) if survey_yaml else None
    for server in list(workout_server_query.fetch()):
        server_name = server['name'][11:]
        server['name'] = server_name
        try:
            snapshots = compute.snapshots().list(project=project, filter=f"name = {server.key.name}*").execute()
            server['snapshots'] = []
            for snapshot in snapshots['items']:
                server['snapshots'].append({'snapshot_name': snapshot['name'], 'creation_date': snapshot['creationTimestamp']})
        except Exception as e:
            pass
        server_list.append(server)
    if registration_required and logged_in_user not in allowed_users:
        return render_template('login.html', auth_config=auth_config)

    if workout:
        assessment_manager = CyberArenaAssessment(workout_id)
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
        if 'assessment' in workout and workout['assessment']:
            assessment = assessment_manager.get_assessment_questions()
        build_now = unit.get('build_now', True)
        if request.method == "POST":
            attempt = assessment_manager.submit()
            return json.dumps(attempt)
        return render_template('fixed_arena_landing_page.html', build_type=build_type, workout=workout,
                               description=unit['description'], container_url=container_url, dns_suffix=dns_suffix,
                               expiration=expiration, shutoff=shutoff, assessment=assessment,
                               is_expired=is_expired, build_now=build_now, auth_config=auth_config, servers=server_list,
                               survey=survey)
    else:
        return redirect('/no-workout')

