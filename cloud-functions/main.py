import time
import calendar
import random
import string
from yaml import load, Loader

from cloud_function_globals import ds_client, project, compute, workout_globals, storage_client
from common.dns_functions import add_dns_record, register_workout_server
from common.datastore_functions import store_unit_info, store_workout_info
from common.stop_workout import stop_workout


# create random strings --> will be used to create random workoutID
def randomStringDigits(stringLength=6):
    return ''.join(random.choice(string.ascii_lowercase) for i in range(stringLength))


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
                                 networkRouting, networks, tags, sshkey=None, guac_path=None):

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


def build_workout(event, context):
    """ Responds to a pub/sub event in which the user has included
    Args:
         event (dict):  The dictionary with data specific to this type of
         event. The `data` field contains the PubsubMessage message. The
         `attributes` field will contain custom attributes if there are any.
         context (google.cloud.functions.Context): The Cloud Functions event
         metadata. The `event_id` field contains the Pub/Sub message ID. The
         `timestamp` field contains the publish time.
    Returns:
        A success status
    """
    pubsub_valid = True
    workout_type = event['attributes']['workout_type'] if 'workout_type' in event['attributes'] else None
    unit_id = event['attributes']['unit_id'] if 'unit_id' in event['attributes'] else None
    num_team = int(event['attributes']['num_team']) if 'num_team' in event['attributes'] else None
    workout_length = int(event['attributes']['length']) if 'length' in event['attributes'] else None
    email = event['attributes']['email'] if 'email' in event['attributes'] else None
    unit_name = event['attributes']['unit_name'] if 'unit_name' in event['attributes'] else None

    if not workout_type or not unit_id or not num_team or not workout_length:
        if context:
            print("""Invalid fields for pubsub message triggered by messageId {} published at {}
            """.format(context.event_id, context.timestamp))
        return False

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
    if num_team > 10:
        num_team = 10

    if workout_length > 7:
        workout_length = 7

    # we have to store each labentry ext IP and send it to the user
    workout_ids = []

    # To do: Pull all of the yaml defaults into a separate function
    if "student_instructions_url" in y['workout']:
        student_instructions_url = y['workout']['student_instructions_url']
    else:
        student_instructions_url = None

    if 'workout_description' in y['workout']:
        workout_description = y['workout']['workout_description']
    else:
        workout_description = None

    ts = str(calendar.timegm(time.gmtime()))
    print("Creating unit %s" % (unit_id))
    store_unit_info(unit_id, email, unit_name, ts, workout_type,
                    student_instructions_url, workout_description)

    # NOTE: Added topic_name and flag entities to store_workout_info() call // For PUBSUB
    for i in range(1, num_team+1):
        generated_workout_ID = randomStringDigits()
        workout_ids.append(generated_workout_ID)
        store_workout_info(
            generated_workout_ID, unit_id, email, workout_length, workout_type,
            ts
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

            tags = None
            if "tags" in server:
                tags = server['tags']

            if "machine_type" in server:
                machine_type = server["machine_type"]
            else:
                machine_type = "n1-standard-1"

            if "network_routing" in server:
                network_routing = server["network_routing"]
            else:
                network_routing = False

            create_instance_custom_image(compute, project, zone, dnszone, generated_workout_ID, server_name, server['image'],
                                         machine_type, network_routing, nics, tags, sshkey, guac_path)

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

    # for i in range(len(list_ext_ip)):
    unit = ds_client.get(ds_client.key('cybergym-unit', unit_id))
    unit['workouts'] = workout_ids
    ds_client.put(unit)

    if context:
        print("""Workout of type {} has completed for user {}. This was triggered by PubSub messageId {} published at {}
        """.format(workout_name, email, context.event_id, context.timestamp))


data = \
        {
            'workout_type': 'cyberattack',
            'unit_id': '123456',
            'num_team': '1',
            'length': '1',
            'email': 'pdhuff@ualr.edu',
            'unit_name': 'Testing JSON'
        }


# Call tested function
event = {'attributes': data}

# For local testing
build_workout(event, None)
