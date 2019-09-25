import os
import time
import calendar
import random
import string
import create_workout
import list_vm
import start_stop_vm

from flask import Flask, render_template, redirect, url_for
from flask import jsonify
from flask import request

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import workoutdescription

# datastore dependency
from google.cloud import datastore

ds_client = datastore.Client()


# create random strings --> will be used to create random workoutID
def randomStringDigits(stringLength=6):
    lettersAndDigits = string.ascii_lowercase + string.digits
    return ''.join(random.choice(lettersAndDigits) for i in range(stringLength))


# --------------------------- FLASK APP --------------------------

# store workout info to google cloud datastore
def store_workout_info(workout_id, user_mail, workout_duration, workout_type, timestamp):
    # create a new user
    new_user = datastore.Entity(ds_client.key('cybergym-workout'))

    new_user.update({
        'workout_ID': workout_id,
        'user_email': user_mail,
        'expiration': workout_duration,
        'type': workout_type,
        'timestamp': timestamp
    })

    # insert a new user
    ds_client.put(new_user)


# send email method
def send_email(user_mail, workout_type, list_ext_IP):
    from_address = 'philiphuff7@gmail.com'
    from_address_cred = 'xnwaiuucpaxzsnys'
    server = smtplib.SMTP('smtp.gmail.com', 587)
    # extended simple mail transfer protocol command sent by an email
    # to identify iterself when connecting to another email server to start
    # the process of sendig an email
    server.ehlo()
    server.starttls()
    server.ehlo()

    server.login(from_address, from_address_cred)

    for (ind, team_url) in enumerate(list_ext_IP):

        body = workoutdescription.body_workout_message(workout_type, team_url)
        mimebody = MIMEText(body, 'html')
        subject = "Team {}: Your UA Little Rock Cyber Gym Workout is Ready!".format(str(ind + 1))
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = from_address
        msg['To'] = user_mail
        msg.attach(mimebody)
        server.sendmail(
            from_address,
            user_mail,
            msg.as_string()
        )

    print('Email has been sent')
    server.quit()


# Application
app = Flask(__name__)


@app.route('/')
def invalid_workout():
    return render_template('no_workout.html')


@app.route('/<workout_type>')
def index(workout_type):
    return render_template('main_page.html', workout_type=workout_type)


@app.route('/team_launcher')
def team_launcher():
    return render_template('team_launcher.html')


@app.route('/workout_done/<build_data>')
def workout_done(build_data):
    return render_template('workout_done.html', build_data=build_data)


@app.route('/listvm')
def list_vm_instances():
    list_vm_test = list_vm.list_instances('ualr-cybersecurity', 'us-central1-a')
    return render_template('list_instances.html', list_vm=list_vm_test)


@app.route('/startvm', methods=['GET', 'POST'])
def start_vm():
    if request.method == 'POST':
        vm = request.get_json()
        print(vm)
        print(vm['instance'])

        start_stop_vm.start_vm(vm['instance'])

        return "vm start"


@app.route('/stopvm', methods=['GET', 'POST'])
def stop_vm():
    if request.method == 'POST':
        vm = request.get_json()
        print(vm)
        print(vm['instance'])

        start_stop_vm.stop_vm(vm['instance'])

        return "vm stop"


@app.route('/update', methods=['GET', 'POST'])
def build_workout():

    if request.method == 'POST':

        # create random number specirfic to the workout (6 characters by default)
        generated_workout_ID = randomStringDigits()

        build_data = request.get_json()
        num_team = int(build_data['team'])

        # we have to store each labentry ext IP and send it to the user
        list_ext_ip = []

        ts = str(calendar.timegm(time.gmtime()))

        store_workout_info(generated_workout_ID, build_data['email'], build_data['length'], build_data['type'], ts)

        for i in range(1, num_team + 1):

            network = 'workout-{}-{}-t{}'.format(ts, generated_workout_ID, i)
            subnetwork = 'lab-{}-{}-t{}'.format(ts, generated_workout_ID, i)

            if (build_data['type'] == 'dos'):
                ext_IP_lab_entry = create_workout.create_dos_workout(network, subnetwork, ts)
                list_ext_ip.append(ext_IP_lab_entry)
                # succesData = {
                #     # 'redirect' : '/workout_done/' + build_data['type'],
                #     'redirect' : ext_IP_lab_entry,
                #     'build_data' : build_data
                # }

                # jsonify is very important for otherwise AJAX succes is not handle correctly
                # return jsonify(succesData)

            if (build_data['type'] == 'cyberattack'):
                ext_IP_lab_entry = create_workout.create_cyberattack_workout(network, subnetwork, ts)
                list_ext_ip.append(ext_IP_lab_entry)

            # future work
            # jsonify is very important for otherwise AJAX succes is not handle correctly
            # return jsonify(succesData)

            if (build_data['type'] == 'spoof'):
                ext_IP_lab_entry = create_workout.create_spoof_workout(network, subnetwork, ts)
                list_ext_ip.append(ext_IP_lab_entry)

            if (build_data['type'] == 'hiddennode'):
                ext_IP_lab_entry = create_workout.create_hiddennode_workout(network, subnetwork, ts)
                list_ext_ip.append(ext_IP_lab_entry)

            if (build_data['type'] == 'ids'):
                ext_IP_lab_entry = create_workout.create_ids_workout(network, subnetwork, ts)
                list_ext_ip.append(ext_IP_lab_entry)

            if (build_data['type'] == 'phishing'):
                ext_IP_lab_entry = create_workout.create_phishing_workout(network, subnetwork, ts)
                list_ext_ip.append(ext_IP_lab_entry)

            if (build_data['type'] == 'theharbor'):
                ext_IP_lab_entry = create_workout.create_theharbor_workout(network, subnetwork, ts)
                list_ext_ip.append(ext_IP_lab_entry)

            if (build_data['type'] == 'hashmyfiles'):
                ext_IP_lab_entry = create_workout.create_hashmyfiles_workout(network, subnetwork, ts)
                list_ext_ip.append(ext_IP_lab_entry)

        send_email(build_data['email'], build_data['type'], list_ext_ip)

        # add time for guacamole setup for each team
        # for i in range(len(list_ext_ip)):
        #     time.sleep(60)

        return "DONE"


if __name__ == '__main__':
     app.run(debug=True, host='0.0.0.0', port=8080)
