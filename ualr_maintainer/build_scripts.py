ds_client = datastore.Client()
compute = googleapiclient.discovery.build('compute', 'v1')
dns_suffix = ".aca-bootcamp.com"
project = 'acapte'

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
                                 networkRouting, networks, tags, metadata=None, sshkey=None, guac_path=None):

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
    compute.zoneOperations().wait(project=project, zone=zone, operation=response["id"]).execute()

    new_instance = compute.instances().get(project=project, zone=zone, instance=name).execute()
    ip_address = None
    if tags:
        for item in tags['items']:
            if item == 'labentry':
                ip_address = new_instance['networkInterfaces'][0]['accessConfigs'][0]['natIP']
                add_dns_record(project, dnszone, workout, ip_address)

    if guac_path:
        register_workout_server(workout, name, guac_path)

    if sshkey:
        ssh_key_body = {
            "items": [
                {
                    "key": "ssh-keys",
                    "value": sshkey
                }
            ],
            "fingerprint": new_instance["metadata"]["fingerprint"]
        }
        request = compute.instances().setMetadata(project=project, zone=zone, instance=name, body=ssh_key_body)
        response = request.execute()