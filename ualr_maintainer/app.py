import datetime
import os
import time
import calendar
import random
import string
import create_workout
import list_vm
import start_stop_vm

import googleapiclient.discovery
from flask import Flask, render_template, redirect, url_for, make_response
from flask import jsonify
from flask import request
from base64 import b64encode as b64
from yaml import load, dump, Loader, Dumper

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import workoutdescription

# datastore dependency
from google.cloud import datastore

ds_client = datastore.Client()
compute = googleapiclient.discovery.build('compute', 'v1')

# create random strings --> will be used to create random workoutID
def randomStringDigits(stringLength=6):
    return ''.join(random.choice(string.ascii_lowercase) for i in range(stringLength))

# ------------------------ FLAG GENERATOR -------------------------
# See also build_flag_startup in create_vm.py for implementation

def flag_generator():
    from os import urandom as rand

    token = b64(rand(12)).decode('UTF-8')
    rand_flag = str('CyberGym{') + token + str('}')

    return rand_flag


# --------------------------- FLASK APP --------------------------

# store workout info to google cloud datastore
def store_workout_info(workout_id, user_mail, workout_duration, workout_type, timestamp, flag):
    # create a new user
    new_workout = datastore.Entity(ds_client.key('cybergym-workout'))

    new_workout.update({
        'workout_ID': workout_id,
        'user_email': user_mail,
        'expiration': workout_duration,
        'type': workout_type,
        'timestamp': timestamp,
        'resources_deleted': False,
        'flag': flag
    })

    # insert a new user
    ds_client.put(new_workout)


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


def create_firewall_rules(project, firewall_rules):
    for rule in firewall_rules:
        # Convert the port specification to the correct json format
        allowed = []
        for port_spec in rule["ports"]:
            protocol, ports = port_spec.split("/")
            if ports == "any":
                addPorts = {"IPProtocol": protocol}
            else:
                portlist = ports.split(",")
                addPorts = {"IPProtocol": protocol, "ports": portlist}
            allowed.append(addPorts)

        firewall_body = {
            "name": rule["name"],
            "network": "https://www.googleapis.com/compute/v1/projects/ualr-cybersecurity/global/networks/" +
                       rule["network"],
            "targetTags": rule["targetTags"],
            "allowed": allowed,
            "sourceRanges": rule["sourceRanges"]
        }
        # If targetTags is None, then we do not want to include it in the insertion request
        if not rule["targetTags"]:
            del firewall_body["targetTags"]

        compute.firewalls().insert(project=project, body=firewall_body).execute()


def create_route(project, zone, route):
    nextHopInstance = "https://www.googleapis.com/compute/v1/projects/" + project + "/zones/" + zone +\
                      "/instances/" + route["nextHopInstance"]
    route_body = {
        "destRange": route["destRange"],
        "name": route["name"],
        "network": "https://www.googleapis.com/compute/v1/projects/ualr-cybersecurity/global/networks/" +
                route["network"],
        "priority": 0,
        "tags": [],
        "nextHopInstance": nextHopInstance
    }
    compute.routes().insert(project=project, body=route_body).execute()


def create_instance_custom_image(compute, project, zone, name, custom_image, machine_type,
                                 networkRouting, networks, tags=None, metadata=None):

    image_response = compute.images().get(project=project, image=custom_image).execute()
    source_disk_image = image_response['selfLink']

    # Configure the machine
    machine = "zones/%s/machineTypes/%s" % (zone, machine_type)

    networkInterfaces = []
    for network in networks:
        if network["external_NAT"]:
            accessConfigs = {'type': 'ONE_TO_ONE_NAT', 'name': 'External NAT'}
        else:
            accessConfigs = None
        add_network_interface = {
            'network': 'projects/ualr-cybersecurity/global/networks/' + network["network"],
            'subnetwork': 'regions/us-central1/subnetworks/' + network["subnet"],
            'networkIP': network["internal_IP"],
            'accessConfigs': [
                accessConfigs
            ]
        }
        networkInterfaces.append(add_network_interface)

    config = {
        'name': name,
        'machineType': machine,

        # allow http and https server with tags
        'tags': tags,

        # Specify the boot disk and the image to use as a source.
        'disks': [
            {
                'boot': True,
                'autoDelete': True,
                'initializeParams': {
                    'sourceImage': source_disk_image,
                }
            }
        ],
        'networkInterfaces': networkInterfaces,
        # Allow the instance to access cloud storage and logging.
        'serviceAccounts': [{
            'email': 'default',
            'scopes': [
                'https://www.googleapis.com/auth/devstorage.read_write',
                'https://www.googleapis.com/auth/logging.write'
            ]
        }],
        # Metadata is readable from the instance and allows you to
        # pass configuration from deployment scripts to instances.
        'metadata': metadata
    }

    # For a network routing firewall (i.e. Fortinet) add an additional disk for logging.
    if networkRouting:
        config["canIpForward"] = True
        image_config = {"name": name + "-disk", "sizeGb": 30,
                        "type": "projects/" + project + "/zones/" + zone + "/diskTypes/pd-ssd"}

        response = compute.disks().insert(project=project, zone=zone, body=image_config).execute()
        compute.zoneOperations().wait(project=project, zone=zone, operation=response["id"]).execute()

        new_disk = {"mode": "READ_WRITE", "boot": False, "autoDelete": True,
                     "source": "projects/" + project + "/zones/" + zone + "/disks/" + name + "-disk"}
        config['disks'].append(new_disk)

    response = compute.instances().insert(project=project, zone=zone, body=config).execute()
    if networkRouting:
        compute.zoneOperations().wait(project=project, zone=zone, operation=response["id"]).execute()


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

        build_data = request.get_json()

        # Open and read YAML file
        yaml_file = "../yaml-files/%s.yaml" % (build_data['type'])

        try:
            f = open(yaml_file, "r")
        except:
            print("File does not exist")

        y = load(f, Loader=Loader)

        workout_name = y['workout']['name']
        project = y['workout']['project_name']
        region = y['workout']['region']
        zone = y['workout']['zone']

        # create random number specific to the workout (6 characters by default)
        generated_workout_ID = randomStringDigits()
        flag = flag_generator()
        num_team = int(build_data['team'])
        if num_team > 10:
            num_team = 10

        build_length = int(build_data['length'])
        if build_length > 7:
            build_length = 7

        # we have to store each labentry ext IP and send it to the user
        list_ext_ip = []

        ts = str(calendar.timegm(time.gmtime()))

        store_workout_info(generated_workout_ID, build_data['email'], build_data['length'], build_data['type'], ts, flag)

        for i in range(1, num_team+1):

            # Create the networks and subnets
            for network in y['networks']:
                network_body = {"name": "%s-%s-%s" % (generated_workout_ID, network['name'], i),
                                "autoCreateSubnetworks": False,
                                "region": "region"}
                response = compute.networks().insert(project=project, body=network_body).execute()
                compute.globalOperations().wait(project=project, operation=response["id"]).execute()

                for subnet in network['subnets']:
                    subnetwork_body = {
                        "name": "%s-%s" % (network_body['name'], subnet['name']),
                        "network": "projects/ualr-cybersecurity/global/networks/" + network_body['name'],
                        "ipCidrRange": subnet['ip_subnet']
                    }
                    response = compute.subnetworks().insert(project=project, region=region,
                                                            body=subnetwork_body).execute()
                    compute.regionOperations().wait(project=project, region=region, operation=response["id"]).execute()

            # Now create the servers
            for server in y['servers']:
                server_name = "%s-%s-%s" % (generated_workout_ID, server['name'], i)
                nics = []
                for n in server['nics']:
                    nic = {
                        "network": "%s-%s-%s" % (generated_workout_ID, n['network'], i),
                        "internal_IP": n['internal_IP'],
                        "subnet": "%s-%s-%s-%s" % (generated_workout_ID, n['network'], i, n['subnet']),
                        "external_NAT": n['external_NAT']
                    }
                    nics.append(nic)
                create_instance_custom_image(compute, project, zone, server_name, server['image'],
                                             server['machine_type'],
                                             server['network_routing'], nics, server['tags'], server['metadata'])

            # Create all of the network routes and firewall rules
            for route in y['routes']:
                r = {"name": "%s-%s-%s" % (generated_workout_ID, route['name'], i),
                     "network": "%s-%s-%s" % (generated_workout_ID, route['network'], i),
                     "destRange": route['dest_range'],
                     "nextHopInstance": "%s-%s-%s" % (generated_workout_ID, route['next_hop_instance'], i)}
                create_route(project, zone, r)

            firewall_rules = []
            for rule in y['firewall_rules']:
                firewall_rules.append({"name": "%s-%s-%s" % (generated_workout_ID, rule['name'], i),
                                       "network": "%s-%s-%s" % (generated_workout_ID, rule['network'], i),
                                       "targetTags": rule['target_tags'],
                                       "protocol": rule['protocol'],
                                       "ports": rule['ports'],
                                       "sourceRanges": rule['source_ranges']})

            create_firewall_rules(project, firewall_rules)

            req = compute.instances().get(project='ualr-cybersecurity', zone='us-central1-a',
                                          instance='%s-cybergym-labentry-%s' % (generated_workout_ID, i))
            response = req.execute()
            ext_IP = response['networkInterfaces'][0]['accessConfigs'][0]['natIP']
            list_ext_ip.append("http://" + ext_IP + ":8080/guacamole/#/client/MgBjAG15c3Fs")

        time.sleep(120)
        # send_email(build_data['email'], build_data['type'], list_ext_ip)

        # add time for guacamole setup for each team
        # for i in range(len(list_ext_ip)):
        key = ds_client.key('workout_resources_track')
        user_register = datastore.Entity(key)
        user_register.update({
                'timestamp_origin': datetime.datetime.now(),
                'user': build_data['email'],
                'workout_type': build_data['type'],
                'ip_list': list_ext_ip,
                'duration': build_data['length'],
                'flag': flag
            })
        ds_client.put(user_register)

        print(list_ext_ip)

        return "DONE"


if __name__ == '__main__':
     app.run(debug=True, host='0.0.0.0', port=8080)
