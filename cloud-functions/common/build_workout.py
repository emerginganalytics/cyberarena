import time
import random
import string

from common.globals import ds_client, project, compute, region, zone, dnszone
from common.dns_functions import add_dns_record, register_workout_server
from common.stop_workout import stop_workout
from common.assessment_functions import get_startup_scripts
from common.networking_functions import create_network, create_route, create_firewall_rules
from common.compute_functions import create_instance_custom_image

# create random strings --> will be used to create random workoutID
def randomStringDigits(stringLength=6):
    return ''.join(random.choice(string.ascii_lowercase) for i in range(stringLength))


def build_workout(workout_id):
    """
    Builds a workout compute environment according to the specification referenced in the datastore with key workout_id
    :param workout_id: The workout_id key in the datastore holding the build specification
    :return: None
    """
    key = ds_client.key('cybergym-workout', workout_id)
    workout = ds_client.get(key)
    # This can sometimes happen when debugging a workout ID and the Datastore record no longer exists.
    if not workout:
        print('No workout for %s exists in the data store' % workout_id)
        return

    # Parse the assessment specification to obtain any startup scripts for the workout.
    startup_scripts = None
    if workout['assessment']:
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
        if startup_scripts and server['name'] in startup_scripts:
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
            create_route(route)

    firewall_rules = []
    for rule in workout['firewall_rules']:
        firewall_rules.append({"name": "%s-%s" % (workout_id, rule['name']),
                               "network": "%s-%s" % (workout_id, rule['network']),
                               "targetTags": rule['target_tags'],
                               "protocol": rule['protocol'],
                               "ports": rule['ports'],
                               "sourceRanges": rule['source_ranges']})

    create_firewall_rules(firewall_rules)

    stop_workout(workout_id)

    workout['complete'] = True
    ds_client.put(workout)


# build_workout('wsjronrgyk')