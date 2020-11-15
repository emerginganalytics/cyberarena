from googleapiclient import discovery

from common.globals import workout_globals, project, zone, dnszone, ds_client, region, SERVER_STATES, SERVER_ACTIONS, \
    PUBSUB_TOPICS, compute


def fortinet_manager_build(workout_id):
    """
    Used to build the fortimanager licensing server for workouts involving the Fortimanager
    :param workout_id: The ID of the build
    :return: None
    """
    compute_beta = discovery.build('compute', 'beta')
    source_machine_image = f"projects/ualr-cybersecurity/global/machineImages/image-fortimanager"
    config = {
        'name': f"{workout_id}-fortimanager",
        'machineType': f"zones/{zone}/machineTypes/n1-standard-2",
        'networkInterfaces': [
            {
                "network": f"projects/{project}/global/networks/{workout_id}-external-network",
                "networkIP": "10.1.0.100",
                "subnetwork": f"regions/{region}/subnetworks/{workout_id}-external-network-default",
                "accessConfigs": []
            }
        ]
    }

    i = 0
    build_success = False
    while not build_success and i < 5:
        workout_globals.refresh_api()
        try:
            response = compute_beta.instances().insert(project=project, zone=zone, body=config,
                                                       sourceMachineImage=source_machine_image).execute()
            build_success = True
            print(f'Sent job to build {workout_id}-fortimanager, and waiting for response')
        except BrokenPipeError:
            i += 1
