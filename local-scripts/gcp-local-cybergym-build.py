#
# This is a test rewrite of the google cloud build in preparation to move the configuration over to a yaml file
# Here are a few good resources for understanding and testing the Google Cloud API
# - https://cloud.google.com/compute/docs/reference/rest/v1 - Use this to test the API
# - https://cloud.google.com/sdk/gcloud/reference - The SDK is good when troubleshooting. It may provide back
#       more information
#

import googleapiclient.discovery
import random, string
from datetime import datetime, timedelta, date
from google.cloud import datastore
import calendar
import time
from google.cloud import datastore
from yaml import load, dump, Loader, Dumper

ds_client = datastore.Client()
compute = googleapiclient.discovery.build('compute', 'v1')

# store workout info to google cloud datastore
def store_workout_info(workout_id, user_mail, workout_duration, workout_type, timestamp):
    # create a new user
    new_workout = datastore.Entity(ds_client.key('cybergym-workout'))

    new_workout.update({
        'workout_ID': workout_id,
        'user_email': user_mail,
        'expiration': workout_duration,
        'type': workout_type,
        'timestamp': timestamp,
        'resources_deleted': False
    })

    # insert a new user
    ds_client.put(new_workout)


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


def test_full_create_workout(yaml_file):
    # Open and read YAML file
    f = open(yaml_file, "r")
    y = load(f, Loader=Loader)

    workout_name = y['workout']['name']
    project = y['workout']['project_name']
    region = y['workout']['region']
    zone = y['workout']['zone']

    generated_workout_ID = ''.join(random.choice(string.ascii_lowercase) for i in range(6))

    # Store the workout information in the cloud data store. This will be used to delete the workout after a day
    ts = str(calendar.timegm(time.gmtime()))
    store_workout_info(generated_workout_ID, "pdhuff@ualr.edu", 1, workout_name, ts)

    # Create the networks and subnets
    for network in y['networks']:
        network_body = {"name": "%s-%s" %(generated_workout_ID, network['name']),
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
            response = compute.subnetworks().insert(project=project, region=region, body=subnetwork_body).execute()
            compute.regionOperations().wait(project=project, region=region, operation=response["id"]).execute()

    # Now create the servers
    for server in y['servers']:
        server_name = "%s-%s" % (generated_workout_ID, server['name'])
        nics = []
        for n in server['nics']:
            nic = {
                "network": "%s-%s" % (generated_workout_ID, n['network']),
                "internal_IP": n['internal_IP'],
                "subnet": "%s-%s" % (generated_workout_ID, n['subnet']),
                "external_NAT": n['external_NAT']
            }
            nics.append(nic)
        create_instance_custom_image(compute, project, zone, server_name, server['image'], server['machine_type'],
                                     server['network_routing'], nics, server['tags'], server['metadata'])

    # Create all of the network routes and firewall rules
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

test_full_create_workout("../yaml-files/test.yaml")
