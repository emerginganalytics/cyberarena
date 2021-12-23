from common.globals import ds_client, project
from common.dns_functions import add_active_directory_dns


def create_dns_forwarding(build_id, ip_address, network):
    """
    Creates DNS forwarding rules for workouts with Active Directory servers. This script is useful
    until a new build operation can be tested.
    :@param unit_id: The unit_id to delete
    :@param ip_address: The IP address of the domain controller.
    :@param network: The name of the network to add in the forwarding rule.
    """
    query_workouts = ds_client.query(kind='cybergym-workout')
    query_workouts.add_filter('unit_id', '=', build_id)
    for workout in list(query_workouts.fetch()):
        workout_project = workout.get('build_project_location', project)
        if workout_project == project:
            workout_id = workout.key.name
            add_active_directory_dns(build_id=workout_id, ip_address=ip_address, network=f"{workout_id}-{network}")
