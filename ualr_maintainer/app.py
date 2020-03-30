import time
import calendar
import random
import string
import list_vm
import start_workout
import threading

from stop_workout import stop_workout
from start_workout import start_workout
from reset_workout import reset_workout
from workout_firewall_update import student_firewall_add
from globals import ds_client, dns_suffix, project, compute, workout_globals, storage_client, logger

import googleapiclient.discovery
from flask import Flask, render_template, redirect, request
from base64 import b64encode as b64
from yaml import load, Loader

from forms import CreateWorkoutForm

# pubusub dependency
from google.cloud import pubsub_v1

# datastore dependency
from google.cloud import datastore

# create random strings --> will be used to create random workoutID
def randomStringDigits(stringLength=6):
    return ''.join(random.choice(string.ascii_lowercase) for i in range(stringLength))


# ------------------------ FLAG GENERATOR -------------------------
def flag_generator():
    from os import urandom as rand

    token = b64(rand(12)).decode('UTF-8')
    rand_flag = str('CyberGym{') + token + str('}')

    return rand_flag


# TODO Identify where to call create_pub_sub_topic() and create_subscriber()
# Create Workout Topic Based on ID and Type[Name]
def create_workout_topic(workout_id, workout_type):
    publisher = pubsub_v1.PublisherClient()

    topic_name = '{}-{}-workout'.format(workout_id, workout_type)
    topic_path = publisher.topic_path(project, topic_name)

    topic = publisher.create_topic(topic_path)
    print('Topic created: {}'.format(topic))
    return topic_name


# Creates the Subscription for each Workout Topic
def create_subscription(topic_name):
    subscriber = pubsub_v1.SubscriberClient()

    # topic_name = '{}-{}-workout'.format(workout_id, workout_type)
    topic_path = subscriber.topic_path(project, topic_name)

    subscription_path = subscriber.subscription_path(
        project, topic_name
    )

    endpoint = '%spush' % (request.url_root)

    push_config = pubsub_v1.types.PushConfig(push_endpoint=endpoint)

    subscriber.create_subscription(
        subscription_path, topic_path, push_config
    )

    def callback(message):
        print("Received message: {}".format(message.data))
        if message.attributes:
            print("Attributes:")
            for key in message.attributes:
                value = message.attributes.get(key)
                print('{}: {}'.format(key, value))
        message.ack()

    future = subscriber.subscribe(subscription_path, callback)

    return subscription_path


# --------------------------- FLASK APP --------------------------
def store_instructor_info(email):
    new_instructor = datastore.Entity(ds_client.key('cybergym-instructor', email))

    new_instructor.update({
        "units": []
    })

    ds_client.put(new_instructor)

def store_unit_info(id, email, name, ts, workout_type, description, student_instructions_url):

    new_unit = datastore.Entity(ds_client.key('cybergym-unit', id))

    new_unit.update({
        "name": name,
        "instructor_id": email,
        "timestamp": ts,
        "workout_type": workout_type,
        "description": description,
        "student_instructions_url": student_instructions_url,
        "workouts": []
    })

    ds_client.put(new_unit)


# This function queries and returns all workout IDs for a given unit
def get_unit_workouts(unit_id):
    unit_workouts = ds_client.query(kind='cybergym-workout')
    unit_workouts.add_filter("unit_id", "=", unit_id)
    workout_list = []
    for workout in list(unit_workouts.fetch()):
        workout_list.append(workout.key.name)

    return workout_list

# NOTICE: Added topic_name and flag entities to store_workout_info()

# store workout info to google cloud datastore
def store_workout_info(workout_id, unit_id, user_mail, workout_duration, workout_type, timestamp, topic_name, subscription_path, flag):
    # create a new user
    new_workout = datastore.Entity(ds_client.key('cybergym-workout', workout_id))

    new_workout.update({
        'unit_id': unit_id,
        'user_email': user_mail,
        'expiration': workout_duration,
        'type': workout_type,
        'start_time': timestamp,
        'run_hours': 0,
        'timestamp': timestamp,
        'resources_deleted': False,
        'running': False,
        'servers': [],
        'topic_name': topic_name,
        'subscription_path': subscription_path,
        'flag': flag
    })

    # insert a new user
    ds_client.put(new_workout)


# Create a new DNS record for the server and
def add_dns_record(project, dnszone, workout_id, ip_address):
    service = googleapiclient.discovery.build('dns', 'v1')

    change_body = {"additions": [
        {
            "kind": "dns#resourceRecordSet",
            "name": workout_id + dns_suffix + ".",
            "rrdatas": [ip_address],
            "type": "A",
            "ttl": 30
        }
    ]}

    request = service.changes().create(project=project, managedZone=dnszone, body=change_body)
    response = request.execute()

    key = ds_client.key('cybergym-workout', workout_id)
    workout = ds_client.get(key)
    workout["external_ip"] = ip_address
    ds_client.put(workout)


# Add the information to the datastore for later management
def register_workout_server(workout_id, server, guac_path):
    key = ds_client.key('cybergym-workout', workout_id)
    workout = ds_client.get(key)
    workout["servers"].append({"server": server, "guac_path": guac_path})
    ds_client.put(workout)


def print_workout_info(workout_id):
    key = ds_client.key('cybergym-workout', workout_id)
    workout = ds_client.get(key)
    for server in workout["servers"]:
        if server["server"] == workout_id + "-cybergym-labentry":
            print("%s: http://%s:8080/guacamole/#/client/%s" %(workout_id, server["ip_address"],
                                                               workout['labentry_guac_path']))



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
            "network": "https://www.googleapis.com/compute/v1/projects/%s/global/networks/%s" % (project, rule["network"]),
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
        "network": "https://www.googleapis.com/compute/v1/projects/%s/global/networks/%s" % (project, route["network"]),
        "priority": 0,
        "tags": [],
        "nextHopInstance": nextHopInstance
    }
    compute.routes().insert(project=project, body=route_body).execute()


def create_instance_custom_image(compute, project, zone, dnszone, workout, name, custom_image, machine_type,
                                 networkRouting, networks, tags, metadata, sshkey=None, guac_path=None):

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
            'network': 'projects/%s/global/networks/%s' % (project, network["network"]),
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

    if sshkey:
        config['metadata']['items'].append({
                    "key": "ssh-keys",
                    "value": sshkey
                })

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
    try:
        compute.zoneOperations().wait(project=project, zone=zone, operation=response["id"]).execute()
    except:
        compute.zoneOperations().wait(project=project, zone=zone, operation=response["id"]).execute()

    new_instance = compute.instances().get(project=project, zone=zone, instance=name).execute()
    ip_address = None
    if tags:
        if 'items' in tags:
            for item in tags['items']:
                if item == 'labentry':
                    ip_address = new_instance['networkInterfaces'][0]['accessConfigs'][0]['natIP']
                    add_dns_record(project, dnszone, workout, ip_address)

    if guac_path:
        register_workout_server(workout, name, guac_path)

# Application
app = Flask(__name__)

app.config['SECRET_KEY'] = 'XqLx4yk8ZW9uukSCXIGBm0RFFJKKyDDm'

@app.route('/')
def invalid_workout():
    return render_template('no_workout.html')


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


@app.route('/team_launcher')
def team_launcher():
    return render_template('team_launcher.html')


@app.route('/workout_done/<build_data>')
def workout_done(build_data):
    return render_template('workout_done.html', build_data=build_data)


@app.route('/listvm')
def list_vm_instances():
    list_vm_test = list_vm.list_instances(project, 'us-central1-a')
    return render_template('list_instances.html', list_vm=list_vm_test)


@app.route('/update', methods=['GET', 'POST'])
def build_workout(build_data, workout_type):

    # Open and read YAML file
    print('Loading config file')
    # get bucket with name
    bucket = storage_client.get_bucket(workout_globals.yaml_bucket)
    # get bucket data as blob
    blob = bucket.get_blob(workout_globals.yaml_folder + workout_type + ".yaml")
    if blob == None:
        return False
    # convert to string
    yaml_from_bucket = blob.download_as_string()
    y = load(yaml_from_bucket, Loader=Loader)

    workout_name = y['workout']['name']
    region = y['workout']['region']
    zone = y['workout']['zone']
    dnszone = y['workout']['dnszone']

    # create random number specific to the workout (6 characters by default)
    flag = flag_generator()
    num_team = int(build_data.team.data)
    if num_team > 10:
        num_team = 10

    build_length = int(build_data.length.data)
    if build_length > 7:
        build_length = 7

    # we have to store each labentry ext IP and send it to the user
    workout_ids = []

    # To do: Pull all of the yaml defaults into a separate function
    if "student_instructions_url" in y['workout']:
        student_instructions_url = y['workout']['student_instructions_url']
    else:
        student_instructions_url = None

    ts = str(calendar.timegm(time.gmtime()))
    unit_id = randomStringDigits()
    print("Creating unit %s" % (unit_id))
    store_unit_info(unit_id, build_data.email.data, build_data.unit.data, ts, workout_type,
                    student_instructions_url, y['workout']['workout_description'])

    # NOTE: Added topic_name and flag entities to store_workout_info() call // For PUBSUB
    for i in range(1, num_team+1):
        generated_workout_ID = randomStringDigits()
        workout_ids.append(generated_workout_ID)
        topic_name = create_workout_topic(generated_workout_ID, workout_type)
        sub_path = create_subscription(topic_name)
        store_workout_info(
            generated_workout_ID, unit_id, build_data.email.data, build_data.length.data, workout_type,
            ts, topic_name, sub_path, flag
        )
        print('Creating workout id %s' % (generated_workout_ID))
        # Create the networks and subnets
        print('Creating networks')
        for network in y['networks']:
            network_body = {"name": "%s-%s" % (generated_workout_ID, network['name']),
                            "autoCreateSubnetworks": False,
                            "region": region}
            response = compute.networks().insert(project=project, body=network_body).execute()
            compute.globalOperations().wait(project=project, operation=response["id"]).execute()
            time.sleep(10)
            for subnet in network['subnets']:
                subnetwork_body = {
                    "name": "%s-%s" % (network_body['name'], subnet['name']),
                    "network": "projects/%s/global/networks/%s" % (project, network_body['name']),
                    "ipCidrRange": subnet['ip_subnet']
                }
                response = compute.subnetworks().insert(project=project, region=region,
                                                        body=subnetwork_body).execute()
                compute.regionOperations().wait(project=project, region=region, operation=response["id"]).execute()

        # Now create the servers
        print('Creating servers')
        for server in y['servers']:
            server_name = "%s-%s" % (generated_workout_ID, server['name'])
            nics = []
            for n in server['nics']:
                nic = {
                    "network": "%s-%s" % (generated_workout_ID, n['network']),
                    "internal_IP": n['internal_IP'],
                    "subnet": "%s-%s-%s" % (generated_workout_ID, n['network'], n['subnet']),
                    "external_NAT": n['external_NAT']
                }
                nics.append(nic)

            # The ssh keys are included with some servers for local authentication within the network
            sshkey = None
            if "sshkey" in server:
                sshkey = server["sshkey"]

            guac_path = None
            if "guac_path" in server:
                guac_path = server['guac_path']

            if "machine_type" in server:
                machine_type = server["machine_type"]
            else:
                machine_type = "n1-standard-1"

            if "network_routing" in server:
                network_routing = server["network_routing"]
            else:
                network_routing = False

            meta = {}
            if "metadata" not in server or server['metadata'] == 'None' \
                    or server['metadata'] == 'none' \
                    or server['metadata'] == None:
                meta = {"items": [
                    {"key": 'topic',
                    "value": topic_name}]}
            else:
                meta = server['metadata']
                meta['items'].append({"key": 'topic',
                                      "value": topic_name})

            create_instance_custom_image(compute, project, zone, dnszone, generated_workout_ID, server_name, server['image'],
                                         machine_type, network_routing, nics, server['tags'],
                                         meta, sshkey, guac_path)

        # Create all of the network routes and firewall rules
        print('Creating network routes and firewall rules')
        if 'routes' in y and y['routes']:
            for route in y['routes']:
                r = {"name": "%s-%s" % (generated_workout_ID, route['name']),
                     "network": "%s-%s" % (generated_workout_ID, route['network']),
                     "destRange": route['dest_range'],
                     "nextHopInstance": "%s-%s" % (generated_workout_ID, route['next_hop_instance'])}
                create_route(project, zone, r)

        firewall_rules = []
        for rule in y['firewall_rules']:
            firewall_rules.append({"name": "%s-%s" % (generated_workout_ID, rule['name']),
                                   "network": "%s-%s" % (generated_workout_ID, rule['network']),
                                   "targetTags": rule['target_tags'],
                                   "protocol": rule['protocol'],
                                   "ports": rule['ports'],
                                   "sourceRanges": rule['source_ranges']})

        create_firewall_rules(project, firewall_rules)

        stop_workout(generated_workout_ID)

    # send_email(build_data['email'], build_data['type'], list_ext_ip)

    # for i in range(len(list_ext_ip)):
    unit = ds_client.get(ds_client.key('cybergym-unit', unit_id))
    unit['workouts'] = workout_ids
    ds_client.put(unit)

    return unit_id

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

        topic = 'projects/%s/topics/%s' % (project, workout['topic_name'])

        return render_template('landing_page.html', description=unit['description'], dns_suffix=dns_suffix,
                                   guac_path=guac_path, expiration=expiration, instructions=student_instructions_url, shutoff=shutoff, workout_id=workout_id, topic=topic,
                                   running=workout['running'])
    else:
        return render_template('no_workout.html')

@app.route('/workout_list/<unit_id>', methods=['GET', 'POST'])
def workout_list(unit_id):
    unit = ds_client.get(ds_client.key('cybergym-unit', unit_id))
    workout_list = get_unit_workouts(unit_id)

    if unit and len(workout_list) > 0:
        return render_template('workout_list.html', workout_list=workout_list, unit_id=unit_id, workout_type=unit['workout_type'])
    else:
        return render_template('no_workout.html')

# TODO: add student_firewall_update call after workout starts
@app.route('/start_vm', methods=['GET', 'POST'])
def start_vm():
    if (request.method == 'POST'):
        workout_id = request.form['workout_id']
        workout = ds_client.get(ds_client.key('cybergym-workout', workout_id))
        if 'time' not in request.form:
            workout['run_hours'] = 2
        else:
            workout['run_hours'] = min(int(request.form['time']), workout_globals.MAX_RUN_HOURS)
        ds_client.put(workout)

        try:
            start_workout(workout_id)
        except:
            compute = workout_globals.refresh_api()
            start_workout(workout_id)
        return redirect("/landing/%s" % (workout_id))

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

# For debugging of pub/sub
@app.route('/publish', methods=['GET', 'POST'])
def publish():
    if (request.method == 'POST'):
        topic = request.form['topic']
        workout_id = request.form['workout_id']
        publish_client = pubsub_v1.PublisherClient()
        publish_client.publish(topic, b'This is a test', test='true')
    return redirect("/landing/%s" % (workout_id))

if __name__ == '__main__':
     app.run(debug=True, host='0.0.0.0', port=8080)
