from flask import Blueprint, request, redirect
from utilities.datastore_functions import *
from utilities.pubsub_functions import *
from utilities.globals import ds_client, log_client, LOG_LEVELS
from utilities.vuln_manager import VulnManager
import json

teacher_api = Blueprint('teacher_api', __name__, url_prefix='/api')


@teacher_api.route('/<unit_id>/vuln/build', methods=['POST'])
def vuln_builder_form_data(unit_id):
    """POST to this endpoint to build form based on filtered items"""
    unit = ds_client.get(ds_client.key("cybergym-unit", unit_id))
    pass


@teacher_api.route('/<unit_id>/vuln/status', methods=['POST'])
def vuln_status(unit_id):
    """Handles polling on injected vulnerabilities or attacks"""
    pass


@teacher_api.route('/<unit_id>/vuln/results/filter', methods=['POST'])
def vuln_results_filter(unit_id):
    """Handles filtering of attack result table -- Possibly unneeded"""
    pass


@teacher_api.route('/vuln/templates/filter', methods=['POST'])
def vuln_template_filter():
    yaml_str = VulnManager().load_yaml_str
    attack_types = ['scanning', 'credential', 'exploitation']
    if request.method == 'POST':
        template_filter = request.json['filter_str']
        print(template_filter)
        if template_filter in attack_types:
            templates = []
            for template in yaml_str['attack']:
                if template['attack_type'] == template_filter:
                    templates.append(template)
            return json.dumps({'attack': templates})
        else:
            return f'Invalid filter item {template_filter}'
    else:
        return '400'


@teacher_api.route('/change_student_name/<workout_id>', methods=["POST"])
def change_student_name(workout_id):
    workout = ds_client.get(ds_client.key("cybergym-workout", workout_id))
    if request.values['new_name']:
        workout['student_name'] = request.values['new_name']
        g_logger = log_client.logger('teacher-app')
        g_logger.log_struct(
            {
                "message": "Workout {} student name changed to {}".format(str(workout_id), str(request.values['new_name']))
            }, severity=LOG_LEVELS.INFO
        )
        ds_client.put(workout)
        return workout['student_name']
    else:
        return False

@teacher_api.route('/create_new_class', methods=['POST'])
def create_new_class():
    if(request.method == 'POST'):
        teacher_email = request.form['teacher_email']
        num_students = request.form['num_students']
        class_name = request.form['class_name']
        student_auth = request.form['student_auth']
        g_logger = log_client.logger('teacher-app')
        g_logger.log_struct(
            {
                "message": "User {} created a new class with {} students".format(teacher_email, num_students)
            }, severity=LOG_LEVELS.INFO
        )
        store_class_info(teacher_email, num_students, class_name, student_auth)

        return redirect('/teacher/home')


@teacher_api.route('/change_roster_name/<class_id>/<student_name>', methods=['POST'])
def change_roster_name(class_id, student_name):
    if request.method == 'POST':
        request_data = request.get_json(force=True)
        new_name = request_data['new_name']
        class_info = ds_client.get(ds_client.key('cybergym-class', int(class_id)))
        if student_name in class_info['roster'] and new_name:
            class_info['roster'].remove(student_name)
            class_info['roster'].append(new_name)
        ds_client.put(class_info)
        if 'unit_list' in class_info:
            for unit in class_info['unit_list']:
                student_workout_query = ds_client.query(kind='cybergym-workout')
                student_workout_query.add_filter('unit_id', '=', unit['unit_id'])
                student_workout_query.add_filter('student_name', '=', student_name)
                for workout in list(student_workout_query.fetch()):
                    workout['student_name'] = new_name
                    ds_client.put(workout)
    return json.dumps(class_info)


@teacher_api.route('/change_class_roster/<class_id>', methods=['POST'])
def change_class_roster(class_id):
    class_info = ds_client.get(ds_client.key('cybergym-class', int(class_id)))
    if request.method == 'POST':
        request_data = request.get_json(force=True)
        if request_data['action'] == 'remove':
            if class_info['student_auth'] == 'email':
                for student in class_info['roster']:
                    if student['student_name'] == request_data['student_name']:
                        class_info['roster'].remove(student)
            if request_data['student_name'] in class_info['roster']:
                class_info['roster'].remove(str(request_data['student_name']))
                g_logger = log_client.logger('teacher-app')
                g_logger.log_struct(
                    {
                        "message": "Student {} removed from class {}".format(request_data['student_name'], class_id)
                    }, severity=LOG_LEVELS.INFO
                )
        elif request_data['action'] == 'add':
            if 'student_auth' not in class_info:
                class_info['student_auth'] = 'anonymous'
                ds_client.put(class_info)
            if class_info['student_auth'] == 'email':
                student_dict = {
                    'student_name': request_data['student_name'],
                    'student_email': request_data['student_email']
                }
                class_info['roster'].append(student_dict)
                user_list = ds_client.get(ds_client.key('cybergym-admin-info', 'cybergym'))
                if request_data['student_email'] not in user_list['students']:
                    user_list['students'].append(request_data['student_email'])
                    ds_client.put(user_list)

            else:
                class_info['roster'].append(str(request_data['student_name']))
            g_logger = log_client.logger('teacher-app')
            g_logger.log_struct(
                {
                    "message": "Student {} added to class {}".format(request_data['student_name'], class_id)
                }, severity=LOG_LEVELS.INFO
            )
        ds_client.put(class_info)
    return redirect('/teacher/home')


@teacher_api.route('add_multiple_students', methods=['POST'])
def add_multiple_students():
    if request.method == "POST":
        request_data = request.get_json(force=True)
        class_id = request_data['class_id']
        new_student_list = request_data['new_student_list'].splitlines()
        user_list = ds_client.get(ds_client.key('cybergym-admin-info', 'cybergym'))

        class_entity = ds_client.get(ds_client.key('cybergym-class', int(class_id)))
        if class_entity['student_auth'] == 'email':
            for student in new_student_list:
                student_info = student.split(',')
                student_name = student_info[0]
                student_email = student_info[1].strip()
                if len(student_name) == 0 or len(student_email) == 0:
                    return json.dumps({"result": "Student entry must have both a name and email address"})
                if '@' not in student_email:
                    return json.dumps({'result': 'Must enter a valid email for student {}.\nEntered email {}'.format(student_name, student_email)})
                new_student_info = {
                    'student_email': student_email,
                    'student_name': student_name
                }
                class_entity['roster'].append(new_student_info)
                if student_email not in user_list['students']:
                    user_list['students'].append(student_email)
            ds_client.put(user_list)
        else:
            for student in new_student_list:
                if student == '' or student == ' ':
                    return json.dumps({'result': 'Student names must not be empty'})
                else:
                    class_entity['roster'].append(student)
        ds_client.put(class_entity)
        return json.dumps({'result': "success"})


@teacher_api.route('/unclaim_workout/<workout_id>', methods=["POST"])
def unclaim_workout(workout_id):
    workout = ds_client.get(ds_client.key("cybergym-workout", workout_id))
    if(request.method == 'POST'):
        if workout:
            if('runtime_counter' in workout and workout['runtime_counter']):
                g_logger = log_client.logger('teacher-app')
                g_logger.log_struct(
                    {
                        "message": "Workout {} is not new, fully rebuilding workout to unclaim".format(str(workout_id))
                    }, severity=LOG_LEVELS.INFO
                )
                pub_nuke_workout(workout_id)
            else:
                workout['student_name'] = ""
                ds_client.put(workout)
                g_logger = log_client.logger('teacher-app')
                g_logger.log_struct(
                    {
                        "message": "Workout {} is new, setting to unclaimed".format(str(workout_id))
                    }, severity=LOG_LEVELS.INFO
                )

        return workout['student_name']


@teacher_api.route('/add_team/<arena_id>', methods=['POST'])
def add_team(arena_id):
    arena = ds_client.get(ds_client.key('cybergym-unit', str(arena_id)))
    if request.method == "POST":
        request_data = request.get_json(force=True)
        new_team_name = request_data['team_name']
        if 'teams' in arena:
            if new_team_name not in arena:
                arena['teams'].append(new_team_name)
        else:
            arena['teams'] = []
            arena['teams'].append(new_team_name)
    ds_client.put(arena)
    return json.dumps(arena)


#Used to change teams for arena workouts
@teacher_api.route('/change_team/<workout_id>', methods=['POST'])
def change_team(workout_id):
    if request.method == "POST":
        request_data = request.get_json(force=True)
        workout = ds_client.get(ds_client.key('cybergym-workout', str(workout_id)))
        if 'new_team' in request_data:
            workout['team'] = request_data['new_team']
            ds_client.put(workout)
            return json.dumps(workout)


@teacher_api.route('/remove_unit_from_class/<class_id>/<unit_id>', methods=['GET','POST'])
def remove_unit_from_class(class_id, unit_id):
    class_info = ds_client.get(ds_client.key('cybergym-class', int(class_id)))
    for unit in class_info['unit_list']:
        if unit['unit_id'] == unit_id:
            class_info['unit_list'].remove(unit)
    ds_client.put(class_info)
    g_logger = log_client.logger('teacher-app')
    g_logger.log_struct(
        {
            "message": "Class {} removed from unit {}".format(class_id, unit_id),
            "class_id": str(class_id),
            "unit": str(unit_id)
        }, severity=LOG_LEVELS.INFO
    )
    return redirect('/teacher_home')


@teacher_api.route('/remove_class/<class_id>', methods=['GET',"POST"])
def remove_class(class_id):
    class_entity = ds_client.get(ds_client.key('cybergym-class', int(class_id)))
    if class_entity:
        g_logger = log_client.logger('teacher-app')
        g_logger.log_struct(
            {
                "message": "Class {} deleted".format(class_entity['class_name']),
                "class_roster": class_entity['roster'],
                "instructor_email": class_entity['teacher_email']
            }, severity=LOG_LEVELS.INFO
        )
        ds_client.delete(ds_client.key('cybergym-class', int(class_id)))

    return redirect('/teacher/home')