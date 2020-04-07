import time
import list_vm
import start_workout

from stop_workout import stop_workout
from start_workout import start_workout
from reset_workout import reset_workout
from globals import ds_client, dns_suffix, project, workout_globals
from workout_build_functions import build_workout
from datastore_functions import get_unit_workouts
from identity_aware_proxy import certs, get_metadata, validate_assertion, audience

from flask import Flask, render_template, redirect, request
from forms import CreateWorkoutForm

# --------------------------- FLASK APP --------------------------

app = Flask(__name__)

app.config['SECRET_KEY'] = 'XqLx4yk8ZW9uukSCXIGBm0RFFJKKyDDm'

# TODO: add something at default route to direct users to correct workout?
# Default route
@app.route('/')
def default_route():
    assertion = request.headers.get('X-Goog-IAP-JWT-Assertion')
    email, id = validate_assertion(assertion)
    page = "<h1>Hello {}</h1>".format(email)
    return page

# Workout build route
@app.route('/<workout_type>', methods=['GET', 'POST'])
def index(workout_type):
    form=CreateWorkoutForm()
    if form.validate_on_submit():
        unit_id = build_workout(form, workout_type)
        if unit_id == False:
            return render_template('no_workout.html')
        url = '/workout_list/%s' % (unit_id)
        return redirect(url)
    return render_template('main_page.html', form=form, workout_type=workout_type)

# TODO: Is this still in use?
@app.route('/team_launcher')
def team_launcher():
    return render_template('team_launcher.html')

# TODO: Is this still in use?
@app.route('/workout_done/<build_data>')
def workout_done(build_data):
    return render_template('workout_done.html', build_data=build_data)

# TODO: Is this still in use?
@app.route('/listvm')
def list_vm_instances():
    list_vm_test = list_vm.list_instances(project, 'us-central1-a')
    return render_template('list_instances.html', list_vm=list_vm_test)

# Student landing page route. Displays information and links for an individual workout
@app.route('/landing/<workout_id>', methods=['GET', 'POST'])
def landing_page(workout_id):
    workout = ds_client.get(ds_client.key('cybergym-workout', workout_id))
    unit = ds_client.get(ds_client.key('cybergym-unit', workout['unit_id']))

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
        if 'student_instructions_url' in unit:
            student_instructions_url = unit['student_instructions_url']

        topic = None
        if 'topic_name' in workout:
            topic = 'projects/%s/topics/%s' % (project, workout['topic_name'])

        return render_template('landing_page.html', description=unit['description'], dns_suffix=dns_suffix,
                                   guac_path=guac_path, expiration=expiration, instructions=student_instructions_url, shutoff=shutoff, workout_id=workout_id, topic=topic,
                                   running=workout['running'])
    else:
        return render_template('no_workout.html')

# Instructor landing page. Displays information and links for a unit of workouts
@app.route('/workout_list/<unit_id>', methods=['GET', 'POST'])
def workout_list(unit_id):
    unit = ds_client.get(ds_client.key('cybergym-unit', unit_id))
    workout_list = get_unit_workouts(unit_id)

    if unit and len(workout_list) > 0:
        return render_template('workout_list.html', workout_list=workout_list, unit_id=unit_id, workout_type=unit['workout_type'])
    else:
        return render_template('no_workout.html')

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
            start_workout(workout_id)
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
            workout = ds_client.get(ds_client.key('cybergym-workout', workout_id))
            if 'time' not in request.form:
                workout['run_hours'] = 2
            else:
                workout['run_hours'] = min(int(request.form['time']), workout_globals.MAX_RUN_HOURS)
            ds_client.put(workout)

            try:
                start_workout(workout_id)
            except:
                workout_globals.refresh_api()
                start_workout(workout_id)

        return redirect("/workout_list/%s" % (unit_id))

# Called by stop workouts button on instructor landing page. Stops all workouts
@app.route('/stop_all', methods=['GET', 'POST'])
def stop_all():
    if (request.method == 'POST'):
        unit_id = request.form['unit_id']
        workout_list = get_unit_workouts(unit_id)
        for workout_id in workout_list:
            try:
                stop_workout(workout_id)
            except:
                compute = workout_globals.refresh_api()
                stop_workout(workout_id)
        return redirect("/workout_list/%s" % (unit_id))

# Called by reset workouts button on instructor landing page. Resets all workouts.
@app.route('/reset_all', methods=['GET', 'POST'])
def reset_all():
    if (request.method == 'POST'):
        unit_id = request.form['unit_id']
        workout_list = get_unit_workouts(unit_id)
        for workout_id in workout_list:
            try:
                reset_workout(workout_id)
            except:
                workout_globals.refresh_api()
                reset_workout(workout_id)
        return redirect("/workout_list/%s" % (unit_id))

# Pub/sub subscription route. Accepts messages from pub/sub server, updates workout datastore, and returns acknowledgement.
@app.route('/push', methods=['POST'])
def get_push():
    return 'OK', 200

# For debugging of pub/sub
from google.cloud import pubsub_v1
@app.route('/publish', methods=['GET', 'POST'])
def publish():
    if (request.method == 'POST'):
        topic = request.form['topic']
        workout_id = request.form['workout_id']
        publish_client = pubsub_v1.PublisherClient()
        publish_client.publish(topic, ('%s-workout complete!' % (workout_id)).encode(), workout_id=workout_id)
    return redirect("/landing/%s" % (workout_id))

if __name__ == '__main__':
     app.run(debug=True, host='0.0.0.0', port=8080)
