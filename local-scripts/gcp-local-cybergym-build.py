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
                addPorts = {"IPProtocol": protocol, "ports": ports}
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
                                 canIpForward, networks, tags=None, metadata=None, wait=False):

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
        'canIpForward': canIpForward,
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

    response = compute.instances().insert(project=project, zone=zone, body=config).execute()
    if wait:
        compute.zoneOperations().wait(project=project, zone=zone, operation=response["id"]).execute()


def test_full_create_workout(project, region, zone):
    generated_workout_ID = ''.join(random.choice(string.ascii_lowercase) for i in range(6))

    # Store the workout information in the cloud data store. This will be used to delete the workout after a day
    ts = str(calendar.timegm(time.gmtime()))
    store_workout_info(generated_workout_ID, "pdhuff@ualr.edu", 1, "test-fortinet-ad", ts)

    # Create the networks and subnets
    external_network = {
        "name": '{}-external-network'.format(generated_workout_ID),
        "ip-subnet": "10.1.0.0/24"
    }
    internal_network = {
        "name": '{}-internal-network'.format(generated_workout_ID),
        "ip-subnet": "10.1.1.0/24"
    }
    dmz_network = {
        "name": '{}-dmz-network'.format(generated_workout_ID),
        "ip-subnet": "10.1.2.0/24"
    }

    networks = [external_network, internal_network, dmz_network]

    for network in networks:
        network_body = {"name": network["name"], "autoCreateSubnetworks": False, "region": "region"}
        response = compute.networks().insert(project=project, body=network_body).execute()
        compute.globalOperations().wait(project=project, operation=response["id"]).execute()

        subnetwork_body = {
            "name": network["name"] + "-default",
            "network": "projects/ualr-cybersecurity/global/networks/" + network["name"],
            "ipCidrRange": network["ip-subnet"]
        }
        response = compute.subnetworks().insert(project=project, region=region, body=subnetwork_body).execute()
        compute.regionOperations().wait(project=project, region=region, operation=response["id"]).execute()

    # Now create the servers
    lab_entry_server = {
        "name": "{}-{}".format(generated_workout_ID, "cybergym-labentry"),
        "image": "image-labentry",
        "machine_type": "n1-standard-1",
        "network_routing": False,
        "nics": [
            {"network": external_network["name"], "internal_IP": "10.1.0.2",
             "subnet": external_network["name"] + "-default", "external_NAT": True}
        ],
        "tags": {"items": ["http-server"]},
        "metadata": None,
        "wait": False
    }

    active_directory_server = {
        "name": "{}-{}".format(generated_workout_ID, "cybergym-ad-dc"),
        "image": "image-cybergym-activedirectory-domaincontroller",
        "machine_type": "n1-standard-2",
        "network_routing": False,
        "nics": [
            {"network": internal_network["name"], "internal_IP": "10.1.1.2",
             "subnet": internal_network["name"] + "-default", "external_NAT": False}
        ],
        "tags": {"items": ["ad-server", "rdp-server"]},
        "metadata": None,
        "wait": False
    }

    fortinet_firewall = {
        "name": "{}-{}".format(generated_workout_ID, "cybergym-fortinet-fortigate"),
        "image": "image-cybergym-fortinet-fortigate1",
        "machine_type": "n1-standard-4",
        "network_routing": True,
        "nics": [
            {"network": external_network["name"], "internal_IP": "10.1.0.10",
             "subnet": external_network["name"] + "-default", "external_NAT": True},
            {"network": internal_network["name"], "internal_IP": "10.1.1.10",
             "subnet": internal_network["name"] + "-default", "external_NAT": False},
            {"network": dmz_network["name"], "internal_IP": "10.1.2.10",
             "subnet": dmz_network["name"] + "-default", "external_NAT": False}
        ],
        "tags": {"items": ["firewall-server", "http-server"]},
        "metadata": None,
        "wait": True
    }

    serverlist = [lab_entry_server, active_directory_server, fortinet_firewall]

    for server in serverlist:
        if server["network_routing"]:
            canIPForward = True
        else:
            canIPForward = False
        create_instance_custom_image(compute, project, zone, server["name"], server["image"], server["machine_type"],
                                     canIPForward, server["nics"], server["tags"], server["metadata"],
                                     server["wait"])

    # Create all of the network routes and firewall rules
    internal_route = {"name": generated_workout_ID + "-default-internal-fortinet", "network": internal_network["name"],
                      "destRange": "0.0.0.0/0", "nextHopInstance": fortinet_firewall["name"]}
    dmz_route = {"name": generated_workout_ID + "-default-dmz-fortinet", "network": dmz_network["name"],
                 "destRange": "0.0.0.0/0", "nextHopInstance": fortinet_firewall["name"]}
    external_to_internal_route = {"name": generated_workout_ID + "-external-to-internal",
                                  "network": external_network["name"], "destRange": "10.1.1.0/24",
                                  "nextHopInstance": fortinet_firewall["name"]}
    external_to_dmz_route = {"name": generated_workout_ID + "-external-to-dmz",
                                  "network": external_network["name"], "destRange": "10.1.2.0/24",
                                  "nextHopInstance": fortinet_firewall["name"]}

    routes = [internal_route, dmz_route, external_to_internal_route, external_to_dmz_route]
    for route in routes:
        create_route(project, zone, route)

    firewall_rules = [
        {"name": generated_workout_ID + "-allow-http", "network": external_network["name"],
         "targetTags": "http-server", "ports": ["tcp/80,8080,443"], "sourceRanges": ["0.0.0.0/0"]},
        {"name": generated_workout_ID + "-allow-all-local-external", "network": external_network["name"],
         "targetTags": None, "protocol": "tcp", "ports": ["tcp/any", "udp/any", "icmp/any"],
         "sourceRanges": ["10.1.0.0/16"]},
        {"name": generated_workout_ID + "-allow-all-local-internal", "network": internal_network["name"],
         "targetTags": None, "protocol": "tcp", "ports": ["tcp/any", "udp/any", "icmp/any"],
         "sourceRanges": ["10.1.0.0/16"]},
        {"name": generated_workout_ID + "-allow-all-local-dmz", "network": dmz_network["name"],
         "targetTags": None, "protocol": "tcp", "ports": ["tcp/any", "udp/any", "icmp/any"],
         "sourceRanges": ["10.1.0.0/16"]}
    ]
    create_firewall_rules(project, firewall_rules)


test_full_create_workout('ualr-cybersecurity', 'us-central1', 'us-central1-a')
