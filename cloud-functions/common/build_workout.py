import time
import random
import string

from common.globals import ds_client, project, compute, region, zone, BUILD_STATES
from common.assessment_functions import get_startup_scripts
from common.networking_functions import create_route, create_firewall_rules, workout_route_setup
from common.prepare_compute import create_instance_custom_image, build_guacamole_server
from common.state_transition import state_transition, check_ordered_workout_state

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

    startup_scripts = None
    # Parse the assessment specification to obtain any startup scripts for the workout.
    if 'state' not in workout or not workout['state']:
        state_transition(entity=workout, new_state=BUILD_STATES.START)

    if workout['assessment']:
        startup_scripts = get_startup_scripts(workout_id=workout_id, assessment=workout['assessment'])
    # Create the networks and subnets
    if check_ordered_workout_state(workout, BUILD_STATES.BUILDING_NETWORKS):
        state_transition(entity=workout, new_state=BUILD_STATES.BUILDING_NETWORKS)
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
                state_transition(entity=workout, new_state=BUILD_STATES.COMPLETED_NETWORKS)

    # Now create the server configurations
    if check_ordered_workout_state(workout, BUILD_STATES.BUILDING_SERVERS):
        state_transition(entity=workout, new_state=BUILD_STATES.BUILDING_SERVERS)
        print('Creating servers')
        for server in workout['servers']:
            custom_image = server['image'] if 'image' in server else None
            build_type = server["build_type"] if 'build_type' in server else None
            machine_image = server["machine_image"] if "machine_image" in server else None
            server_name = "%s-%s" % (workout_id, server['name'])
            sshkey = server["sshkey"]
            tags = server['tags']
            machine_type = server["machine_type"]
            network_routing = server["network_routing"]
            min_cpu_platform = server["minCpuPlatform"] if "minCpuPlatform" in server else None
            add_disk = server["add_disk"] if "add_disk" in server else None
            nics = []
            for n in server['nics']:
                n['external_NAT'] = n['external_NAT'] if 'external_NAT' in n else False
                nic = {
                    "network": f"{workout_id}-{n['network']}",
                    "internal_IP": n['internal_IP'],
                    "subnet": f"{workout_id}-{n['network']}-{n['subnet']}",
                    "external_NAT": n['external_NAT']
                }
                # Nested VMs are sometimes used for vulnerable servers. This adds those specified IP addresses as
                # aliases to the NIC
                if 'IP_aliases' in n and n['IP_aliases']:
                    alias_ip_ranges = []
                    for ipaddr in n['IP_aliases']:
                        alias_ip_ranges.append({"ipCidrRange": ipaddr})
                    nic['aliasIpRanges'] = alias_ip_ranges
                nics.append(nic)
            # Add the startup script for assessment as metadata if it exists
            meta_data = None
            if startup_scripts and server['name'] in startup_scripts:
                meta_data = startup_scripts[server['name']]
    
            create_instance_custom_image(compute=compute, workout=workout_id, name=server_name,
                                         custom_image=custom_image, machine_type=machine_type,
                                         networkRouting=network_routing, networks=nics, tags=tags,
                                         meta_data=meta_data, sshkey=sshkey, minCpuPlatform=min_cpu_platform,
                                         build_type=build_type, machine_image=machine_image, add_disk=add_disk)

        state_transition(entity=workout, new_state=BUILD_STATES.COMPLETED_SERVERS)
    # Create the student entry guacamole server
    if check_ordered_workout_state(workout, BUILD_STATES.BUILDING_STUDENT_ENTRY):
        state_transition(entity=workout, new_state=BUILD_STATES.BUILDING_STUDENT_ENTRY)
        if workout['student_entry']:
            network_name = f"{workout_id}-{workout['student_entry']['network']}"
            student_entry_username = workout['student_entry']['username'] if 'username' in workout['student_entry'] else None
            rdp_domain = workout['student_entry']['domain'] if 'domain' in workout['student_entry'] else None
            security_mode = workout['student_entry']['security-mode'] if 'security-mode' in workout['student_entry'] else 'nla'
            guac_connection = [{
                'workout_id': workout_id,
                'entry_type': workout['student_entry']['type'],
                'ip': workout['student_entry']['ip'],
                'username': student_entry_username,
                'password': workout['student_entry']['password'],
                'domain': rdp_domain,
                'security-mode': security_mode
            }]
            build_guacamole_server(build=workout, network=network_name,
                                   guacamole_connections=guac_connection)
            # Get the workout key again or the state transition will overwrite it
            workout = ds_client.get(ds_client.key('cybergym-workout', workout_id))
        else:
            state_transition(entity=workout, new_state=BUILD_STATES.BROKEN)
            return
        state_transition(entity=workout, new_state=BUILD_STATES.COMPLETED_STUDENT_ENTRY)
    # Create all of the network routes and firewall rules
    if check_ordered_workout_state(workout, BUILD_STATES.BUILDING_ROUTES):
        state_transition(entity=workout, new_state=BUILD_STATES.BUILDING_ROUTES)
        print('Creating network routes and firewall rules')
        if 'routes' in workout and workout['routes']:
            workout_route_setup(workout_id)

    if check_ordered_workout_state(workout, BUILD_STATES.BUILDING_FIREWALL):
        state_transition(entity=workout, new_state=BUILD_STATES.BUILDING_FIREWALL)
        firewall_rules = []
        for rule in workout['firewall_rules']:
            firewall_rules.append({"name": "%s-%s" % (workout_id, rule['name']),
                                   "network": "%s-%s" % (workout_id, rule['network']),
                                   "targetTags": rule['target_tags'],
                                   "protocol": rule['protocol'],
                                   "ports": rule['ports'],
                                   "sourceRanges": rule['source_ranges']})
    
        create_firewall_rules(firewall_rules)
