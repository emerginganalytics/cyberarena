import time

from common.globals import project, compute, region, zone, ds_client, log_client


def create_firewall_rules(firewall_rules):
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


def create_route(route):
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


def workout_route_setup(workout_id):
    key = ds_client.key('cybergym-workout', workout_id)
    workout = ds_client.get(key)
    g_logger = log_client.logger(workout_id)

    if 'routes' in workout and workout['routes']:
        for route in workout['routes']:
            router = compute.instances().get(project=project, zone=zone,
                                             instance=f"{workout_id}-{route['next_hop_instance']}").execute()
            i = 0
            while (not router and 'name' not in router) and i < 50:
                time.sleep(10)
                i += 1
                router = compute.instances().get(project=project, zone=zone,
                                                 instance=f"{workout_id}-{route['next_hop_instance']}").execute()
            if i >= 50:
                g_logger.log_text(f"Timeout waiting to add routes for {route['next_hop_instance']}")
                return False

            r = {"name": "%s-%s" % (workout_id, route['name']),
                 "network": "%s-%s" % (workout_id, route['network']),
                 "destRange": route['dest_range'],
                 "nextHopInstance": "%s-%s" % (workout_id, route['next_hop_instance'])}

            create_route(r)


def create_network(networks, build_id):
    """
    Build the network for the given build specification
    :param networks: A specification of networks and subnetwork to build
    :param build_id: The ID of the build. This will be used for referencing the build by name in the future.
    :return:
    """
    for network in networks:
        network_body = {"name": "%s-%s" % (build_id, network['name']),
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
