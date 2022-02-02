import json
from flask import Blueprint, jsonify, redirect, render_template, request, session
from forms.forms import CreateWorkoutForm
from utilities.reset_workout import reset_workout
from utilities.stop_workout import stop_workout
from utilities.child_project_manager import ChildProjectManager
from utilities.infrastructure_as_code.build_spec_to_cloud import BuildSpecToCloud, InvalidBuildSpecification
from utilities.datastore_functions import *
from utilities.globals import auth_config, dns_suffix, ds_client, log_client, logger, LOG_LEVELS, main_app_url, \
    post_endpoint, workout_token, workout_globals, BuildTypes
from utilities.pubsub_functions import *
from utilities.workout_validator import WorkoutValidator
from utilities.yaml_functions import generate_yaml_content, parse_workout_yaml, save_yaml_file

from teacher_app.teacher_api import teacher_api

teacher_app = Blueprint('teacher_app', __name__, url_prefix="/teacher", static_folder="../static", template_folder="templates")
teacher_app.register_blueprint(teacher_api)

@teacher_app.route('/home', methods=['GET', 'POST'])
def teacher_home():
    if 'user_email' in session:
        
        teacher_email = session['user_email']
        try:
            teacher_info = ds_client.get(ds_client.key('cybergym-instructor', str(teacher_email)))
            if not teacher_info:
               add_new_teacher(teacher_email)
        except:
            add_new_teacher(teacher_email)
            
        unit_list = ds_client.query(kind='cybergym-unit')
        unit_list.add_filter("instructor_id", "=", str(teacher_email))

        class_list = ds_client.query(kind='cybergym-class')
        class_list.add_filter('teacher_email', '=', str(teacher_email))

        teacher_info = {}
        current_units = []
        expired_units = []
        teacher_classes = []
        for unit in list(unit_list.fetch()):
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
        current_units = sorted(current_units, key = lambda i: (i['timestamp']), reverse=True)
        expired_units = sorted(expired_units, key = lambda i: (i['timestamp']), reverse=True)
        for class_instance in list(class_list.fetch()):
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

        #Get list of workouts from cloud bucket
        build_workout_options = []
        yaml_bucket = storage_client.get_bucket(workout_globals.yaml_bucket)
        for blob in yaml_bucket.list_blobs(prefix=workout_globals.yaml_folder):
            blob_name = blob.name
            formatted_blobname = blob_name.replace(workout_globals.yaml_folder, "").split('.')[0]
            if formatted_blobname != "":
                build_workout_options.append(formatted_blobname)

        return render_template('teacher_home.html', auth_config=auth_config, teacher_info=teacher_info, workout_titles=build_workout_options)
    else:
        return render_template('login.html', auth_config=auth_config)


@teacher_app.route('/<workout_type>', methods=['GET', 'POST'])
def index(workout_type):
    logger.info('Request for workout type %s' % workout_type)
    yaml_check = WorkoutValidator(workout_type=workout_type).yaml_check()
    if yaml_check:
        form = CreateWorkoutForm()
    else:
        return render_template('404.html')
    if request.method == "POST":
        unit_name = request.form['unit_name']
        length = request.form['length']
        email = request.form['email']
        build_now = request.form.get("build_now")
        build_now = True if build_now else False
        build_count = 0
        class_name = None
        # If team is indicated, then the teacher intends to build this for anonymous authentication.
        # Otherwise, a class registration is required.
        if request.form['team'] != "":  
            build_count = int(request.form['team'])
            registration_required = False
        else:
            class_name = request.form['class_target']
            class_query = ds_client.query(kind='cybergym-class')
            class_query.add_filter('teacher_email', '=', str(email))
            class_query.add_filter('class_name', '=', str(class_name))
            class_list = list(class_query.fetch())
            build_count = len(class_list)
            for class_object in class_list:
                class_entity = class_object
            if class_entity['student_auth'] == 'email':
                registration_required = True
            else:
                registration_required = False

        try:
            cloud_spec = BuildSpecToCloud(cyber_arena_yaml=workout_type, unit_name=unit_name,
                                            build_count=build_count, class_name=class_name, workout_length=length,
                                            email=email, build_now=build_now,
                                            registration_required=registration_required, time_expiry=None)
        except InvalidBuildSpecification:
            return render_template('invalid_build_specification.html')
        spec_results = cloud_spec.commit_to_cloud()
        unit_id = spec_results.get('unit_id', None)
        build_type = spec_results.get('build_type', None)

        # Valid build_type and images
        if build_type == BuildTypes.COMPUTE:
            if build_now:
                pm = ChildProjectManager(unit_id)
                pm.build_workouts()
            url = f'/teacher/workout_list/{unit_id}'
            return redirect(url)
        elif build_type == BuildTypes.ARENA:
            # There is not currently logic to build an arena across multiple projects
            publisher = pubsub_v1.PublisherClient()
            topic_path = publisher.topic_path(project, workout_globals.ps_build_arena_topic)
            publisher.publish(topic_path, data=b'Competition Cyber Arena', unit_id=unit_id)
            url = '/teacher/arena_list/%s' % (unit_id)
            return redirect(url)
        elif build_type == BuildTypes.CONTAINER:
            url = '/teacher/workout_list/%s' % (unit_id)
            return redirect(url)

    return render_template('main_page.html', workout_type=workout_type, auth_config=auth_config)


# Instructor landing page. Displays information and links for a unit of workouts
@teacher_app.route('/workout_list/<unit_id>', methods=['GET', 'POST'])
def workout_list(unit_id):
    unit = ds_client.get(ds_client.key('cybergym-unit', unit_id))
    build_type = unit['build_type']
    workout_list = get_unit_workouts(unit_id)
    registration_required = unit.get('registration_required', False)
    if not registration_required:
        workout_list = sorted(workout_list, key=lambda i: (i['student_name']))
    else:
        workout_list = sorted(workout_list, key=lambda i: (i['student_name']['student_name']))
    teacher_instructions_url = None
    if 'teacher_instructions_url' in unit:
        teacher_instructions_url = unit['teacher_instructions_url']

    #For updating individual workout ready state
    if (request.method=="POST"):
        if build_type == 'arena':
            return json.dumps(unit)
        return json.dumps(workout_list)    
    
    if unit and len(str(workout_list)) > 0:
        return render_template('workout_list.html', workout_list=workout_list, unit=unit,
                               teacher_instructions=teacher_instructions_url, main_app_url=main_app_url)
    else:
        return render_template('no_workout.html')


@teacher_app.route('/arena_list/<unit_id>', methods=['GET', 'POST'])
def arena_list(unit_id):
    unit = ds_client.get(ds_client.key('cybergym-unit', unit_id))

    arena_query = ds_client.query(kind='cybergym-workout')
    arena_query.add_filter("unit_id", "=", unit_id)
    workout_list = list(arena_query.fetch())
    
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
    if (request.method=="POST"):
        return json.dumps(unit)

    if unit:
        return render_template('arena_list.html', unit_teams=unit_teams, teacher_instructions=teacher_instructions_url, workout_list=workout_list,
                            student_instructions=student_instructions_url, description=unit['description'], unit_id=unit_id, start_time=start_time)


# Called by start workouts button on instructor landing. Starts all workouts in a unit.
@teacher_app.route('/start_all', methods=['GET', 'POST'])
def start_all():
    if (request.method == 'POST'):
        unit_id = request.form['unit_id']
        workout_list = get_unit_workouts(unit_id)
        for workout_id in workout_list:
            workout = ds_client.get(ds_client.key('cybergym-workout', workout_id['name']))
            if 'time' not in request.form:
                workout['run_hours'] = 2
            else:
                workout['run_hours'] = min(int(request.form['time']), workout_globals.MAX_RUN_HOURS)
            ds_client.put(workout)

            pub_start_vm(workout_id['name'])

        g_logger = log_client.logger('teacher-app')
        g_logger.log_struct(
            {
                "message": "Unit {} started by teacher".format(unit_id),
                "unit": str(unit_id),
                "runtime": str(workout['run_hours'])
            }, severity=LOG_LEVELS.INFO
        )
        return redirect("/teacher/workout_list/%s" % (unit_id))


@teacher_app.route('/start_arena', methods=['GET', 'POST'])
def start_arena():
    if request.method == 'POST':
        unit_id = request.form['unit_id']
        arena_unit = ds_client.get(ds_client.key('cybergym-unit', unit_id))
        if 'time' not in request.form:
            arena_unit['arena']['run_hours'] = 2
        else:
            arena_unit['arena']['run_hours'] = min(int(request.form['time']), workout_globals.MAX_RUN_HOURS)
        for workout in arena_unit['workouts']:
            workout_entity = ds_client.get(ds_client.key('cybergym-workout', workout))
            workout_entity['run_hours'] = arena_unit['arena']['run_hours']
            ds_client.put(workout_entity)
        ds_client.put(arena_unit)
        start_time = time.gmtime(time.time())
        time_string = str(start_time[3]) + ":" + str(start_time[4]) + ":" + str(start_time[5])
        arena_unit['start_time'] = time_string
        ds_client.put(arena_unit)
        pub_start_vm(unit_id, 'start-arena')
        g_logger = log_client.logger('teacher-app')
        g_logger.log_struct(
            {
                "message": "Arena {} started by teacher".format(unit_id),
                "unit": str(unit_id)
            }, severity=LOG_LEVELS.INFO
        )
    return redirect('/teacher/arena_list/%s' % (unit_id))


# Called by stop workouts button on instructor landing page. Stops all workouts
@teacher_app.route('/stop_all', methods=['GET', 'POST'])
def stop_all():
    if (request.method == 'POST'):
        unit_id = request.form['unit_id']
        workout_list = get_unit_workouts(unit_id)
        for workout_id in workout_list:
            try:
                pub_stop_vm(workout_id['name'])
            except:
                compute = workout_globals.refresh_api()
                stop_workout(workout_id['name'])
        g_logger = log_client.logger('teacher-app')
        g_logger.log_struct(
            {
                "message": "Unit {} stopped by teacher".format(unit_id),
                "unit": str(unit_id)
            }, severity=LOG_LEVELS.INFO
        )
        return redirect("/teacher/workout_list/%s" % (unit_id))


# Called by reset workouts button on instructor landing page. Resets all workouts.
@teacher_app.route('/reset_all', methods=['GET', 'POST'])
def reset_all():
    if (request.method == 'POST'):
        unit_id = request.form['unit_id']
        workout_list = get_unit_workouts(unit_id)
        for workout_id in workout_list:
            try:
                reset_workout(workout_id['name'])
            except:
                workout_globals.refresh_api()
                reset_workout(workout_id['name'])
        g_logger = log_client.logger('teacher-app')
        g_logger.log_struct(
            {
                "message": "Unit {} started by student".format(unit_id),
                "unit": str(unit_id)
            }, severity=LOG_LEVELS.INFO
        )
        return redirect("/teacher/workout_list/%s" % (unit_id))


@teacher_app.route('/get_classes', methods=['GET', 'POST'])
def get_classes():
    if request.method == "POST":
        user_data = request.get_json(force=True)
        if 'user_email' in user_data:
            class_query = ds_client.query(kind='cybergym-class')
            class_query.add_filter('teacher_email', '=', str(user_data['user_email']))
            
            class_list = []
            for class_object in list(class_query.fetch()):
                class_list.append(class_object)
            
            return json.dumps(class_list)


@teacher_app.route('/quick_build/<workout_type>', methods=['GET','POST'])
def quick_build(workout_type):
    logger.info('Request for workout type %s' % workout_type)
    yaml_check = WorkoutValidator(workout_type=workout_type).yaml_check()
    if yaml_check(workout_type):
        form = CreateWorkoutForm()
    else:
        return render_template('404.html')
    if request.method == "POST":
        unit_name = workout_type + " QUICK BUILD"
        length = 1
        email = request.form['qb_email']
        team = 1
        class_name = None
        build_now = request.form.get("build_now")
        build_now = True if build_now else False

        yaml_string = parse_workout_yaml(workout_type)
        unit_id, build_type = process_workout_yaml(yaml_string, workout_type, unit_name,
                                                   team, class_name, length, email, build_now=build_now)

        if unit_id == False:
            return render_template('no_workout.html')
        elif build_type == 'compute':
            pub_build_request_msg(unit_id=unit_id, topic_name=workout_globals.ps_build_workout_topic)
            url = '/teacher/workout_list/%s' % (unit_id)
            return redirect(url)
        elif build_type == 'arena':

            pub_build_request_msg(unit_id=unit_id, topic_name=workout_globals.ps_build_arena_topic)
            url = '/teacher/arena_list/%s' % (unit_id)
            return redirect(url)
        elif build_type == 'container':
            url = '/teacher/workout_list/%s' % (unit_id)
            return redirect(url)

        g_logger = log_client.logger('teacher-app')
        g_logger.log_struct(
            {
                "message": "Quick building unit {}".format(unit_id),
                "unit": str(unit_id),
                "teacher": str(email),
                "type": str(workout_type)
            }, severity=LOG_LEVELS.INFO
        )
    return render_template('main_page.html', workout_type=workout_type, auth_config=auth_config)
