from flask import Blueprint, jsonify, redirect, render_template, request, session
from utilities.arena_authorizer import ArenaAuthorizer
from utilities.assessment_functions import CyberArenaAssessment
from utilities.datastore_functions import *
from utilities.globals import auth_config, compute, zone, cloud_log, dns_suffix, ds_client, log_client, logger, LOG_LEVELS, LogIDs, \
    main_app_url, post_endpoint, workout_token
from utilities.pubsub_functions import *
from utilities.workout_validator import WorkoutValidator
from utilities.yaml_functions import YamlFunctions
import json
student_app = Blueprint('student_app', __name__, url_prefix="/student", static_folder="../static",
                        template_folder="templates")


@student_app.route('/home', methods=['GET', 'POST'])
def registered_student_home():
    if 'user_email' in session and 'user_groups' in session:
        student_email = session['user_email']
        if ArenaAuthorizer.UserGroups.STUDENTS not in session['user_groups']:
            return render_template('403.html')

        workout_list = ds_client.query(kind='cybergym-workout')
        workout_list.add_filter("student_email", "=", str(student_email))
        student_workouts = []
        for workout in list(workout_list.fetch()):
            if workout['state'] != BUILD_STATES.DELETED:
                workout_info = {
                    'workout_id': workout.key.name,
                    'workout_name': workout['type'],
                    'timestamp': workout['timestamp']
                }
                student_workouts.append(workout_info)
        student_workouts = sorted(student_workouts, key=lambda i: (i['timestamp']), reverse=True)

        student_info = {'workouts': student_workouts}
        return render_template('student_home.html', auth_config=auth_config, student_info=student_info)
    else:
        return render_template('login.html', auth_config=auth_config)


@student_app.route('/landing/<workout_id>', methods=['GET', 'POST'])
def landing_page(workout_id):
    unit_list = ds_client.query(kind='cybergym-unit')
    workouts_list = list(unit_list.add_filter('workouts', '=', str(workout_id)).fetch())
    if not workouts_list:
        return render_template('404.html')
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
        if(request.method == "POST"):
            attempt = assessment_manager.submit()
            return json.dumps(attempt)
        return render_template('landing_page.html', build_type=build_type, workout=workout,
                               description=unit['description'], container_url=container_url, dns_suffix=dns_suffix,
                               expiration=expiration, shutoff=shutoff, assessment=assessment,
                               is_expired=is_expired, build_now=build_now, auth_config=auth_config, servers=server_list,
                               survey=survey)
    else:
        return render_template('no_workout.html')


@student_app.route('/arena_landing/<workout_id>', methods=['GET', 'POST'])
def arena_landing(workout_id):
    workout = ds_client.get(ds_client.key('cybergym-workout', workout_id))
    unit = ds_client.get(ds_client.key('cybergym-unit', workout['unit_id']))
    arena_server_info = get_arena_ip_addresses_for_workout(workout_id)
    assessment_manager = CyberArenaAssessment(workout_id)
    student_instructions_url = None
    if 'student_instructions_url' in workout:
        student_instructions_url = workout['student_instructions_url']
    formatted_instruction_url = student_instructions_url
    assessment = guac_user = guac_pass = flags_found = None

    if 'workout_user' in workout:
        guac_user = workout['workout_user']
    if 'workout_password' in workout:
        guac_pass = workout['workout_password']
    if 'assessment' in workout:
        try:
            assessment = assessment_manager.get_assessment_questions()
        except TypeError:
            g_logger = log_client.logger('cybergym-app-errors')
            g_logger.log_text("TypeError encountered when submitting assessment for arena {}".format(workout_id), severity=LOG_LEVELS.INFO)

    if(request.method == "POST"):
        attempt = assessment_manager.submit()
        return jsonify(attempt)
       
    return render_template('arena_landing.html', description=unit['description'], unit_id=unit.key.name, assessment=assessment, workout=workout, dns_suffix=dns_suffix, 
                        guac_user=guac_user, guac_pass=guac_pass, arena_id=workout_id, student_instructions=formatted_instruction_url, server_info=arena_server_info)


@student_app.route('/server_management/<workout_id>', methods=['POST'])
def student_server_management(workout_id):
    if request.method == 'POST':
        data = request.json
        if 'action' in data:
            g_logger = log_client.logger('student-app')
            g_logger.log_struct(
                {
                    "message": "{} action called for server {}".format(data['action'], data['server_name'])
                }, severity=LOG_LEVELS.INFO
            )
            pub_manage_server(data['server_name'], data['action'])
    return 'True'


@student_app.route('/feedback/<workout_id>', methods=['POST'])
def student_feedback(workout_id):
    if request.method == 'POST':
        data = request.form
        
        store_student_feedback(data, workout_id)
        return json.dumps(data)


@student_app.route('/<unit_id>/signup', methods=['GET', 'POST'])
def unit_signup(unit_id):
    unit = ds_client.get(ds_client.key('cybergym-unit', unit_id))
    if request.method == 'POST':
        workout_query = ds_client.query(kind='cybergym-workout')
        workout_query.add_filter('unit_id', '=', unit_id)
        claimed_workout = None
        for workout in list(workout_query.fetch()):
            if 'student_name' in workout:
                if workout['student_name'] == None or workout['student_name'] == "":
                    with ds_client.transaction():
                        claimed_workout = workout
                        claimed_workout['student_name'] = request.form['student_name']
                        ds_client.put(claimed_workout)
                        if unit['build_type'] == 'arena':
                            return redirect('/student/arena_landing/%s' % claimed_workout.key.name)
                        else:
                            return redirect('/student/landing/%s' % claimed_workout.key.name)
            else:
                with ds_client.transaction():
                    claimed_workout = workout
                    claimed_workout['student_name'] = request.form['student_name']
                    ds_client.put(claimed_workout)
                    if unit['build_type'] == 'arena':
                        return redirect('/student/arena_landing/%s' % claimed_workout.key.name)
                    else:
                        return redirect('/student/landing/%s' % claimed_workout.key.name)
        return render_template('unit_signup.html', unit_full=True)
    return render_template('unit_signup.html')
