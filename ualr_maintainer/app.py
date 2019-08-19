import os
import time, calendar

import create_workout
import list_vm
import start_stop_vm

from flask import Flask, render_template, redirect, url_for
from flask import jsonify
from flask import request

import smtplib

# --------------------------- FLQSK APP --------------------------

# send email method
def send_email(user_mail, workout_type, list_ext_IP):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    # extended simple mail transfer protocol command sent by an email
    # to identify iterself when connecting to another email server to start
    # the process of sendig an email
    server.ehlo()
    server.starttls()
    server.ehlo()

    server.login('gaetan.verdinpol@gmail.com', 'wohmersychenpiju')

    subject = "Your workout is ready"
    body = "You just created a {} workout for {} team \n\n".format(workout_type, len(list_ext_IP))

    for (ind,team_url) in enumerate(list_ext_IP):
        body += "Team {} : {} \n".format(ind+1, team_url[7:])

    msg = f"Subject: {subject}\n\n{body}"

    server.sendmail(
        'gaetan.verdinpol@gmail.com',
        user_mail,
        msg
    )

    print('Email has been sent')
    server.quit()



# Application

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/workout_done/<build_data>')
def workout_done(build_data):
    return render_template('workout_done.html', build_data = build_data)


@app.route('/listvm')
def list_vm_instances():
    list_vm_test = list_vm.list_instances('ualr-cybersecurity','us-central1-a')
    return render_template('list_instances.html', list_vm = list_vm_test)


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

    if request.method == 'POST':

        build_data = request.get_json()
        num_team = int(build_data['team'])

        # we have to store each labentry ext IP and send it to the user
        list_ext_ip = []

        for i in range (1, num_team+1):

            ts = str(calendar.timegm(time.gmtime()))
            network = 'test-workout-{}-team{}'.format(ts, i)
            subnetwork = 'lab-{}-team{}'.format(ts, i)

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


        # add time for guacamole setup for each team
        # for i in range(len(list_ext_ip)):
        #     time.sleep(60)

        send_email(build_data['email'], build_data['type'], list_ext_ip)

        return "DONE"









### Purpose of the os.environ.get ??? --> why not just choosing a port
# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
