import time
import list_vm
import start_workout
import requests

from stop_workout import stop_workout
from start_workout import start_workout
from reset_workout import reset_workout
from globals import ds_client, dns_suffix, project, workout_globals, logger, workout_token, post_endpoint
from utilities.pubsub_functions import *
from workout_build_functions import build_workout
from datastore_functions import get_unit_workouts
from identity_aware_proxy import certs, get_metadata, validate_assertion, audience
from utilities.yaml_functions import parse_workout_yaml
from utilities.datastore_functions import process_workout_yaml, store_student_uploads, retrieve_student_uploads
from werkzeug.utils import secure_filename
from calendar import timegm
import google.oauth2.id_token
import google.auth.transport.requests
from flask import Flask, render_template, redirect, request, jsonify
from forms import CreateWorkoutForm, CreateExpoForm
import json
# --------------------------- FLASK APP --------------------------

app = Flask(__name__)

app.config['SECRET_KEY'] = 'XqLx4yk8ZW9uukSCXIGBm0RFFJKKyDDm'

# TODO: add something at default route to direct users to correct workout?
# Default route
@app.route('/')
def default_route():
    http_request = google.auth.transport.requests.Request()
    id_token = request.headers['Authorization']
    claims = google.oauth2.id_token.verify_firebase_token(id_token, http_request)
    # assertion = request.headers.get('X-Goog-IAP-JWT-Assertion')
    # email, id = validate_assertion(assertion)
    # return render_template('no_workout.html')
    

# Workout build route
@app.route('/<workout_type>', methods=['GET', 'POST'])
def index(workout_type):
    logger.info('Request for workout type %s' % workout_type)
    form = CreateWorkoutForm()
    if form.validate_on_submit():
        yaml_string = parse_workout_yaml(workout_type)
        unit_id, build_type = process_workout_yaml(yaml_string, workout_type, form.unit.data,
                                                     form.team.data, form.length.data, form.email.data)

        if unit_id == False:
            return render_template('no_workout.html')
        elif build_type == 'compute':
            # pub_build_request_msg(unit_id=unit_id, topic_name=workout_globals.ps_build_workout_topic)
            print("workout building")
            url = '/workout_list/%s' % (unit_id)
            return redirect(url)
        elif build_type == 'arena':
            pub_build_request_msg(unit_id=unit_id, topic_name=workout_globals.ps_build_arena_topic)
            url = '/arena_list/%s' % (unit_id)
            return redirect(url)

    return render_template('main_page.html', form=form, workout_type=workout_type)


# Student landing page route. Displays information and links for an individual workout
@app.route('/landing/<workout_id>', methods=['GET', 'POST'])
def landing_page(workout_id):
    workout = ds_client.get(ds_client.key('cybergym-workout', workout_id))
    unit = ds_client.get(ds_client.key('cybergym-unit', workout['unit_id']))
    retrieve_student_uploads(workout_id)
    if (workout):
        expiration = time.strftime('%d %B %Y', (
            time.localtime((int(workout['expiration']) * 60 * 60 * 24) + int(workout['timestamp']))))

        run_hours = int(workout['run_hours'])
        if run_hours == 0:
            shutoff = "expired"
        else:
            shutoff = time.strftime('%d %B %Y at %I:%M %p',
                                    (time.localtime((int(workout['run_hours']) * 60 * 60) + int(workout['start_time']))))

        guac_path = None
        if workout['servers']:
            for server in workout['servers']:
                if server['guac_path'] != None:
                    guac_path = server['guac_path']
        student_instructions_url = None
        if 'student_instructions_url' in workout:
            student_instructions_url = workout['student_instructions_url']

        teacher_instructions_url = None
        if 'teacher_instructions_url' in unit:
            teacher_instructions_url = unit['teacher_instructions_url']

        complete = None
        if 'complete' in workout:
            complete = workout['complete']

        assessment = assessment_type = None
        if 'assessment' in workout:
            assessment = {}
            try:
                question_list = []

                if 'type' in workout['assessment']:
                    assessment_type = workout['assessment']['type']
                for question in workout['assessment']['questions']:
                    question_dict = {}
                    question_dict['question'] = question['question']
                    if(question['type'] == 'input'):
                        if 'answer' in question:
                            question_dict['answer'] = question['answer']
                    question_dict['type'] = question['type']
                    question_list.append(question_dict)
                assessment = question_list
            except TypeError:
                print('assessment not defined')
                print(assessment)

        if(request.method == "POST"):
            valid_answers = []
            num_correct = 0
            for i in range(len(assessment)):
                if(assessment[i].get('type') != 'upload'):
                    valid_answers.append(assessment[i].get('answer'))

            assessment_answers = request.form.getlist('answer')
            assessment_questions = request.form.getlist('question')

            assessment_upload_prompt = request.form.getlist('upload_prompt')
            assessment_uploads = request.files.getlist('file_upload')


            store_student_uploads(workout_id, assessment_uploads)

            for i in range(len(assessment_answers)):
                
                user_input = {
                    "question":assessment_questions[i],
                    "answer":assessment_answers[i]
                }

                # valid_answers.append(assessment[i].get('answer'))
                user_answer = str(user_input['answer'])
                true_answer = str(assessment[i].get('answer'))

                if valid_answers[i]:
                    if(user_answer.lower() == valid_answers[i].lower()):
                        num_correct += 1

            uploaded_files = []
            urls = retrieve_student_uploads(workout_id)
            for index, item in enumerate(assessment_uploads):#range(len(assessment_uploads)):
                user_input = {
                    "question": assessment_upload_prompt[index],
                    "storage_url": urls[index]
                }
                uploaded_files.append(user_input)


            percentage_correct = num_correct / len(assessment_questions) * 100
            workout['uploaded_files'] = uploaded_files
            workout['submitted_answers'] = assessment_answers
            workout['assessment_score'] = percentage_correct
            ds_client.put(workout)

            return render_template('landing_page.html', description=unit['description'], dns_suffix=dns_suffix,
                               guac_path=guac_path, expiration=expiration, student_instructions=student_instructions_url,
                               teacher_instructions=teacher_instructions_url,
                               shutoff=shutoff, workout_id=workout_id, running=workout['running'],
                               complete=complete, workout_type=workout['type'], assessment=assessment, assessment_type=assessment_type,
                               score=percentage_correct)

        return render_template('landing_page.html', description=unit['description'], dns_suffix=dns_suffix,
                               guac_path=guac_path, expiration=expiration, student_instructions=student_instructions_url, 
                               teacher_instructions=teacher_instructions_url,
                               shutoff=shutoff, workout_id=workout_id, running=workout['running'],
                               complete=complete, workout_type=workout['type'], assessment=assessment, assessment_type=assessment_type)
    else:
        return render_template('no_workout.html')

# Instructor landing page. Displays information and links for a unit of workouts
@app.route('/workout_list/<unit_id>', methods=['GET', 'POST'])
def workout_list(unit_id):
    unit = ds_client.get(ds_client.key('cybergym-unit', unit_id))
    build_type = unit['build_type']
    workout_url_path = unit['workout_url_path']
    workout_list = get_unit_workouts(unit_id)
    
    teacher_instructions_url = None
    if 'teacher_instructions_url' in unit:
        teacher_instructions_url = unit['teacher_instructions_url']
    
    student_instructions_url = None
    if 'student_instructions_url' in unit:
        student_instructions_url = unit['student_instructions_url']

    if (request.method=="POST"):
        if build_type == 'arena':
            return json.dumps(unit)
        return json.dumps(workout_list)
        
    
    if unit and len(str(workout_list)) > 0:
        return render_template('workout_list.html', build_type=build_type, workout_url_path=workout_url_path,
                               workout_list=workout_list, unit_id=unit_id,
                               description=unit['description'], teacher_instructions=teacher_instructions_url, student_instructions=student_instructions_url,
                               workout_type=unit['workout_type'])
    else:
        return render_template('no_workout.html')


@app.route('/arena_list/<unit_id>', methods=['GET', 'POST'])
def arena_list(unit_id):
    unit = ds_client.get(ds_client.key('cybergym-unit', unit_id))
    build_type = unit['build_type']
    workout_url_path = unit['workout_url_path']
    workout_list = get_unit_workouts(unit_id)
    
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
    if (request.method=="POST"):
        return json.dumps(unit)

    if unit:
        return render_template('arena_list.html', unit_teams=unit['teams'], teacher_instructions=teacher_instructions_url, workout_list=workout_list,
                            student_instructions=student_instructions_url, description=unit['description'], unit_id=unit_id, start_time=start_time)


@app.route('/arena_landing/<workout_id>', methods=['GET', 'POST'])
def arena_landing(workout_id):
    workout = ds_client.get(ds_client.key('cybergym-workout', workout_id))
    unit = ds_client.get(ds_client.key('cybergym-unit', workout['unit_id']))
    
    student_instructions_url = None
    if 'student_instructions_url' in workout:
        student_instructions_url = workout['student_instructions_url']

    assessment = guac_user = guac_pass = flags_found = None

    if 'workout_user' in workout:
        guac_user = workout['workout_user']
    if 'workout_password' in workout:
        guac_pass = workout['workout_password']
    if 'assessment' in workout:
        try:
            question_list = []

            if 'type' in workout['assessment']:
                assessment_type = workout['assessment']['type']
            for question in workout['assessment']['questions']:
                question_dict = {}
                if(question['type'] == 'input'):
                    if 'answer' in question:
                        question_dict['question'] = question['question']
                        question_dict['answer'] = question['answer']
                        question_dict['type'] = question['type']
                        question_dict['point_value'] = question['points']
                        question_list.append(question_dict)

                #remove already submitted flag prompts to avoid double submission
                if 'submitted_answers' in workout:
                    for question in question_list:
                        for answer_group in workout['submitted_answers']:
                            if answer_group['answer'] == question['answer']:
                                question_list.remove(question)
            assessment = question_list

        except TypeError:
            print('assessment not defined')

    if(request.method == "POST"):
        valid_answers = []
        points = 0
        response = {}
        answer_found = False
        flag_attempt = request.form.get('answer')
        question_key = request.form.get('question_content')
        point_value = int(request.form.get('point_value'))
        for i in range(len(assessment)):
            if question_key == assessment[i].get('question') and flag_attempt == assessment[i].get('answer'):
                answer_found = True
                # if(assessment[i].get('type') != 'upload'):
                # valid_answers.append(assessment[i].get('answer'))
        
        # if flag_attempt in valid_answers:
        if answer_found:
            answer_time = time.gmtime(time.time())
            time_string = str(answer_time[3]) + ":" + str(answer_time[4]) + ":" + str(answer_time[5])
            team_query = ds_client.query(kind='cybergym-workout')
            team_query.add_filter('teacher_email', '=', workout['teacher_email'])
            team_query.add_filter('unit_id', '=', workout['unit_id'])
            team_members = []

            for team_member in list(team_query.fetch()):
                team_members.append(team_member)
            answer_time_dict = {
                'answer': flag_attempt,
                'timestamp': time_string
            }

            #check if the answer is a duplicate
            if 'submitted_answers' in workout:
                if flag_attempt not in workout['submitted_answers']:
                    workout['submitted_answers'].append(answer_time_dict)
                else:
                    response = {
                        'answer_correct': True,
                        'points_gained':0,
                    }
                    return json.dumps(response)

            else:
                workout['submitted_answers'] = []
                workout['submitted_answers'].append(answer_time_dict)
            points += int(point_value)
            response = {
            'answer_correct': True,
            'points_gained': points,   
            }
            #check if this is the first time this flag has been found
            if 'found_flags' in unit:
                if flag_attempt in unit['found_flags']:
                    print("flag already found")
                else:
                    unit['found_flags'].append(flag_attempt)
                    point_value += 50
                    ds_client.put(unit)
            else:
                unit['found_flags'] = []
                unit['found_flags'].append(flag_attempt)
                point_value += 50
                ds_client.put(unit)

            for member in team_members:
                if 'points' in member:
                    prev_score = member['points']
                    prev_score += point_value
                    member['points'] = prev_score
                else:
                    member['points'] = point_value
                member['submitted_answers'] = workout['submitted_answers']
                ds_client.put(member)
        else:
            if flag_attempt in unit['found_flags']:
                response = {
                    'answer_correct': True,
                    'points_gained': 0
                }
                return json.dumps(response)
            else:
                response = {
                    'answer_correct': False, 
                    'points_gained': 0
                }
        return json.dumps(response)

    return render_template('arena_landing.html', description=unit['description'], assessment=assessment, running=workout['running'], unit_id=workout['unit_id'], dns_suffix=dns_suffix, 
                        guac_user=guac_user, guac_pass=guac_pass, arena_id=workout_id, student_instructions=student_instructions_url)

@app.route("/login", methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@app.route("/login_test", methods=['GET', 'POST'])
def login_test():
    http_request = google.auth.transport.requests.Request()
    id_token = request.headers['Authorization']
    email = request.headers['user_email']
    user_name = request.headers['user_name']
    # print(id_token)
    # print("User email: " + email)
    # print("User name: " + user_name)
    claims = google.oauth2.id_token.verify_firebase_token(id_token, http_request)

    if claims:
        if 'name' in claims:
            return claims['name']
        print("claims" + claims)
        return render_template('teacher_home.html', user_name=user_name)
    else:
        return render_template('teacher_home.html', user_name="idk lol")
    return render_template('no_workout.html')

@app.route('/teacher_home', methods=['GET', 'POST'])
def teacher_home():
    print("Logged in successfully")
    return render_template('teacher_home.html')

@app.route('/teacher_info', methods=['GET', 'POST'])
def get_teacher_info():
    if (request.method == "POST"):
        teacher_email = request.get_json()
        unit_list = ds_client.query(kind='cybergym-unit')
        unit_list.add_filter("instructor_id", "=", str(teacher_email['teacher_email']))
        # unit_list.add_filter("resources_deleted", "=", False)
        teacher_units = []
        for unit in list(unit_list.fetch()):
            unit_info = {
                'unit_id': unit.key.name,
                'type': unit['workout_type'],
                'unit_name': unit['unit_name'],
                'timestamp': unit['timestamp']
            }
            teacher_units.append(unit_info)
        teacher_units = sorted(teacher_units, key = lambda i: (i['timestamp']), reverse=True)
    return json.dumps(teacher_units)



# TODO: add student_firewall_update call after workout starts
# Called by start workout buttons on landing pages
@app.route('/start_vm', methods=['GET', 'POST'])
def start_vm():
    if (request.method == 'POST'):
        workout_id = request.form['workout_id']
        workout = ds_client.get(ds_client.key('cybergym-workout', workout_id))
        if 'time' not in request.form:
            workout['run_hours'] = 2
        else:
            workout['run_hours'] = min(int(request.form['time']), workout_globals.MAX_RUN_HOURS)
        workout['running'] = True
        ds_client.put(workout)

        try:
            pub_start_vm(workout_id)
            # start_workout(workout_id)
        except:
            compute = workout_globals.refresh_api()
            start_workout(workout_id)
        return redirect("/landing/%s" % (workout_id))

# Called by stop workout buttons on landing pages
@app.route('/stop_vm', methods=['GET', 'POST'])
def stop_vm():
    if (request.method == 'POST'):
        workout_id = request.form['workout_id']
        try:
            stop_workout(workout_id)
        except:
            compute = workout_globals.refresh_api()
            stop_workout(workout_id)
        return redirect("/landing/%s" % (workout_id))

# Called by reset workout buttons on landing pages
@app.route('/reset_vm', methods=['GET', 'POST'])
def reset_vm():
    if (request.method == 'POST'):
        workout_id = request.form['workout_id']
        try:
            reset_workout(workout_id)
        except:
            compute = workout_globals.refresh_api()
            reset_workout(workout_id)
        return redirect("/landing/%s" % (workout_id))

# Called by start workouts button on instructor landing. Starts all workouts in a unit.
@app.route('/start_all', methods=['GET', 'POST'])
def start_all():
    if (request.method == 'POST'):
        unit_id = request.form['unit_id']
        workout_list = get_unit_workouts(unit_id)
        t_list = []
        for workout_id in workout_list:
            workout = ds_client.get(ds_client.key('cybergym-workout', workout_id['name']))
            if 'time' not in request.form:
                workout['run_hours'] = 2
            else:
                workout['run_hours'] = min(int(request.form['time']), workout_globals.MAX_RUN_HOURS)
            ds_client.put(workout)
            try:
                pub_start_vm(workout_id['name'])
            except:
                workout_globals.refresh_api()
                start_workout(workout_id['name'])

        return redirect("/workout_list/%s" % (unit_id))

@app.route('/start_arena', methods=['GET', 'POST'])
def start_arena():
    if request.method == 'POST':
        unit_id = request.form['unit_id']
        arena_unit = ds_client.get(ds_client.key('cybergym-unit', unit_id))
        if 'time' not in request.form:
            arena_unit['arena']['run_hours'] = 2
        else:
            arena_unit['arena']['run_hours'] = min(int(request.form['time']), workout_globals.MAX_RUN_HOURS)
        ds_client.put(arena_unit)
        start_time = time.gmtime(time.time())
        time_string = str(start_time[3]) + ":" + str(start_time[4]) + ":" + str(start_time[5])
        print(time_string)
        arena_unit['start_time'] = time_string
        ds_client.put(arena_unit)
        pub_start_vm(unit_id, 'start-arena')
    return redirect('/arena_list/%s' % (unit_id))

# Called by stop workouts button on instructor landing page. Stops all workouts
@app.route('/stop_all', methods=['GET', 'POST'])
def stop_all():
    if (request.method == 'POST'):
        unit_id = request.form['unit_id']
        workout_list = get_unit_workouts(unit_id)
        for workout_id in workout_list:
            try:
                stop_workout(workout_id['name'])
            except:
                compute = workout_globals.refresh_api()
                stop_workout(workout_id['name'])
        return redirect("/workout_list/%s" % (unit_id))

# Called by reset workouts button on instructor landing page. Resets all workouts.
@app.route('/reset_all', methods=['GET', 'POST'])
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
        return redirect("/workout_list/%s" % (unit_id))

# Workout completion check. Receives post request from workout and updates workout as complete in datastore.
# Request data in form {'workout_id': workout_id, 'token': token,}
@app.route('/complete', methods=['POST'])
def complete_verification():
    if (request.method == 'POST'):
        workout_request = request.get_json(force=True)

        workout_id = workout_request['workout_id']
        token = workout_request['token']
        workout = ds_client.get(ds_client.key('cybergym-workout', workout_id))

        token_exists = next(item for item in workout['assessment']['questions'] if item['key'] == token)
        token_pos = next((i for i, item in enumerate(workout['assessment']['questions']) if item['key'] == token), None)
        if token_exists:
            logger.info("Completion token matches. Setting the workout question %d to complete." % token_pos)
            workout['assessment']['questions'][token_pos]['complete'] = True
            ds_client.put(workout)
            logger.info('%s workout question %d marked complete.' % (workout_id, token_pos+1))
            return 'OK', 200
        else:
            logger.info("In complete_verification: Completion key %s does NOT exist in assessment dict! Aborting" % token)
    '''
        if (workout_request["token"] == workout_token):
            logger.info("Completion token matches. Setting the workout to complete.")
            workout_id = workout_request["workout_id"]
            workout = ds_client.get(ds_client.key('cybergym-workout', workout_id))
            workout["complete"] = True
            ds_client.put(workout)
            logger.info('%s workout is marked complete.' % workout_id)
            return 'OK', 200
        else:
            logger.info("In complete_verification: Completion token does NOT match! Aborting")
    '''

# For debugging of pub/sub
@app.route('/publish', methods=['GET', 'POST'])
def publish():
    if (request.method == 'POST'):
        workout_id = request.form['workout_id']
        msg = {"token": workout_token,
               "workout_id": workout_id}
        res = requests.post(post_endpoint, json=msg)
        print(res)
    return redirect("/landing/%s" % (workout_id))

@app.route('/privacy', methods=['GET'])
def privacy():
    return render_template('privacy.html')

@app.route('/Xv9RxioJIE0Zdk8FFJh7naJQtVG/<workout_type>', methods=['GET', 'POST'])
def expo(workout_type):
    """ Temporary workout page for the online signature experience expo
    Args:
         Workout_type - The workout name and yaml file name to build
    Returns:
        An expo page for several people to participate in a workout at once.
    """
    form = CreateExpoForm()
    if form.validate_on_submit():
        unit_id = build_workout(form, workout_type)
        if unit_id == False:
            return render_template('no_workout.html')
        url = '/workout_list/%s' % (unit_id)
        return redirect(url)
    return render_template('expo_page.html', form=form, workout_type=workout_type)




if __name__ == '__main__':
     app.run(debug=True, host='0.0.0.0', port=8080, threaded=True)
