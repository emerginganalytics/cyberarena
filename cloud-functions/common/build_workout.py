import time
import random
import string

from common.globals import ds_client, project, compute, region, zone, dnszone
from common.dns_functions import add_dns_record, register_workout_server
from common.stop_workout import stop_workout
from common.assessment_functions import get_startup_scripts

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


def create_instance_custom_image(compute, workout, name, custom_image, machine_type,
                                 networkRouting, networks, tags, meta_data, sshkey=None, guac_path=None):

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

    if meta_data:
        config['metadata'] = {'items': meta_data}
    if sshkey:
        if 'items' in meta_data:
            config['metadata']['items'].append({"key": "ssh-keys", "value": sshkey})
        else:
            config['metadata'] = {'items': {"key": "ssh-keys", "value": sshkey}}

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


def build_workout(workout_id):
    """
    Builds a workout compute environment according to the specification referenced in the datastore with key workout_id
    :param workout_id: The workout_id key in the datastore holding the build specification
    :return: None
    """
    key = ds_client.key('cybergym-workout', workout_id)
    workout = ds_client.get(key)
    # Parse the assessment specification to obtain any startup scripts for the workout.
    startup_scripts = get_startup_scripts(workout_id=workout_id, assessment=workout['assessment'])
    # Create the networks and subnets
    print('Creating networks')
    for network in workout['networks']:
        network_body = {"name": "%s-%s" % (workout_id, network['name']),
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
    for server in workout['servers']:
        server_name = "%s-%s" % (workout_id, server['name'])
        sshkey = server["sshkey"]
        guac_path = server['guac_path']
        tags = server['tags']
        machine_type = server["machine_type"]
        network_routing = server["network_routing"]
        nics = []
        for n in server['nics']:
            nic = {
                "network": "%s-%s" % (workout_id, n['network']),
                "internal_IP": n['internal_IP'],
                "subnet": "%s-%s-%s" % (workout_id, n['network'], n['subnet']),
                "external_NAT": n['external_NAT']
            }
            nics.append(nic)
        # Add the startup script for assessment as metadata if it exists
        meta_data = None
        if server['name'] in startup_scripts:
            meta_data = startup_scripts[server['name']]

        create_instance_custom_image(compute=compute, workout=workout_id, name=server_name,
                                     custom_image=server['image'], machine_type=machine_type,
                                     networkRouting=network_routing, networks=nics, tags=tags,
                                     meta_data=meta_data, sshkey=sshkey, guac_path=guac_path)

    # Create all of the network routes and firewall rules
    print('Creating network routes and firewall rules')
    if 'routes' in workout and workout['routes']:
        for route in workout['routes']:
            r = {"name": "%s-%s" % (workout_id, route['name']),
                 "network": "%s-%s" % (workout_id, route['network']),
                 "destRange": route['dest_range'],
                 "nextHopInstance": "%s-%s" % (workout_id, route['next_hop_instance'])}
            create_route(project, zone, r)

    firewall_rules = []
    for rule in workout['firewall_rules']:
        firewall_rules.append({"name": "%s-%s" % (workout_id, rule['name']),
                               "network": "%s-%s" % (workout_id, rule['network']),
                               "targetTags": rule['target_tags'],
                               "protocol": rule['protocol'],
                               "ports": rule['ports'],
                               "sourceRanges": rule['source_ranges']})

    create_firewall_rules(project, firewall_rules)

    stop_workout(workout_id)

    workout['complete'] = True
    ds_client.put(workout)
