import os
import time
import calendar
import random
import string

import create_workout
import list_vm
import start_stop_vm
from workoutdescription import cyberattack

from flask import Flask, render_template, redirect, url_for
from flask import jsonify
from flask import request

import smtplib

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
        body = str.replace(cyberattack.EMAIL_BODY, "WORKOUT_URL", team_url)
        subject = "Your UA Little Rock Cyber Gym Workout {} is Ready! Forward this email to Team {}".format(
        workout_type, str(ind + 1))
        msg = f"Subject: {subject}\n\n{body}"

        server.sendmail(
            from_address,
            user_mail,
            msg
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
def build_dos_workout():
    print("yo test")

    if request.method == 'POST':

        # create random number specirfic to the workout (6 characters by default)
        generated_workout_ID = randomStringDigits()

        build_data = request.get_json()
        num_team = int(build_data['team'])

        print(build_data)

        # we have to store each labentry ext IP and send it to the user
        list_ext_ip = []

        ts = str(calendar.timegm(time.gmtime()))
        print("timestamp : ", ts)

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

        send_email(build_data['email'], build_data['type'], list_ext_ip)

        # add time for guacamole setup for each team
        # for i in range(len(list_ext_ip)):
        #     time.sleep(60)

        print("YOOO")

        return "DONE"

### Purpose of the os.environ.get ??? --> why not just choosing a port
# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
