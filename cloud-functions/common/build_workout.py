import time
from google.cloud import pubsub_v1
from common.globals import ds_client, log_client, project, compute, region, zone, BUILD_STATES, LOG_LEVELS, \
    PUBSUB_TOPICS, SERVER_ACTIONS, cloud_log, LogIDs
from common.networking_functions import create_route, create_firewall_rules, workout_route_setup
from common.state_transition import state_transition, check_ordered_workout_state
from googleapiclient.errors import HttpError


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
        cloud_log(workout_id, f"The datastore record for {workout_id} no longer exists!", LOG_LEVELS.ERROR)
        raise LookupError

    if 'state' not in workout or not workout['state']:
        state_transition(entity=workout, new_state=BUILD_STATES.START)

    # Create the networks and subnets
    if check_ordered_workout_state(workout, BUILD_STATES.BUILDING_NETWORKS):
        state_transition(entity=workout, new_state=BUILD_STATES.BUILDING_NETWORKS)
        for network in workout['networks']:
            cloud_log(workout_id, f"Building network {workout_id}-{network['name']}", LOG_LEVELS.INFO)
            network_body = {"name": f"{workout_id}-{network['name']}",
                            "autoCreateSubnetworks": False,
                            "region": region}
            try:
                response = compute.networks().insert(project=project, body=network_body).execute()
                compute.globalOperations().wait(project=project, operation=response["id"]).execute()
                time.sleep(10)
            except HttpError as err:
                # If the network already exists, then this may be a rebuild and ignore the error
                if err.resp.status in [409]:
                    pass
            for subnet in network['subnets']:
                cloud_log(workout_id, f"Building the subnetwork {network_body['name']}-{subnet['name']}",
                          LOG_LEVELS.INFO)
                subnetwork_body = {
                    "name": f"{network_body['name']}-{subnet['name']}",
                    "network": "projects/%s/global/networks/%s" % (project, network_body['name']),
                    "ipCidrRange": subnet['ip_subnet']
                }
                try:
                    response = compute.subnetworks().insert(project=project, region=region,
                                                            body=subnetwork_body).execute()
                    compute.regionOperations().wait(project=project, region=region, operation=response["id"]).execute()
                except HttpError as err:
                    # If the subnetwork already exists, then this may be a rebuild and ignore the error
                    if err.resp.status in [409]:
                        pass
            state_transition(entity=workout, new_state=BUILD_STATES.COMPLETED_NETWORKS)

    # Now create the server configurations
    if check_ordered_workout_state(workout, BUILD_STATES.BUILDING_SERVERS):
        state_transition(entity=workout, new_state=BUILD_STATES.BUILDING_SERVERS)
        pubsub_topic = PUBSUB_TOPICS.MANAGE_SERVER
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(project, pubsub_topic)
        for server in workout['servers']:
            server_name = f"{workout_id}-{server['name']}"
            cloud_log(workout_id, f"Sending pubsub message to build {server_name}", LOG_LEVELS.INFO)
            publisher.publish(topic_path, data=b'Server Build', server_name=server_name, action=SERVER_ACTIONS.BUILD)
        # Also build the student entry server for the workout
        publisher.publish(topic_path, data=b'Server Build', server_name=f"{workout_id}-student-guacamole",
                          action=SERVER_ACTIONS.BUILD)
        state_transition(entity=workout, new_state=BUILD_STATES.COMPLETED_SERVERS)
    # Create all of the network routes and firewall rules
    if check_ordered_workout_state(workout, BUILD_STATES.BUILDING_ROUTES):
        state_transition(entity=workout, new_state=BUILD_STATES.BUILDING_ROUTES)
        cloud_log(workout_id, f"Creating network routes and firewall rules for {workout_id}", LOG_LEVELS.INFO)
        if 'routes' in workout and workout['routes']:
            workout_route_setup(workout_id)
    if check_ordered_workout_state(workout, BUILD_STATES.BUILDING_FIREWALL):
        state_transition(entity=workout, new_state=BUILD_STATES.BUILDING_FIREWALL)
        firewall_rules = []
        unique_names = []
        for rule in workout['firewall_rules']:
            if rule['name'] not in unique_names:
                firewall_rules.append({"name": "%s-%s" % (workout_id, rule['name']),
                                       "network": "%s-%s" % (workout_id, rule['network']),
                                       "targetTags": rule['target_tags'],
                                       "protocol": rule['protocol'],
                                       "ports": rule['ports'],
                                       "sourceRanges": rule['source_ranges']})
                unique_names.append(rule['name'])
        create_firewall_rules(firewall_rules)
        state_transition(entity=workout, new_state=BUILD_STATES.COMPLETED_FIREWALL)
    cloud_log(workout_id, f"Finished the build process with a final state: {workout['state']}", LOG_LEVELS.INFO)
