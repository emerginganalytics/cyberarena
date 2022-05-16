import click
from common.globals import ds_client, BUILD_STATES
from common.nuke_workout import nuke_workout
from common.state_transition import state_transition


@click.command()
@click.argument('build_id')
@click.argument('server_name')
@click.argument('type')
@click.argument('parameters')
def fix_server_in_unit(build_id, server_name, type, parameters):
    """
    Fixes a server when something goes wrong in the unit
    :@param unit_id: The unit_id to delete
    :@param server: The server in the unit to act on
    :@param type: The type of fix. The following types are supported
            - ssh-key - Include the new public sshkey as a parameter
            - image-correction - Include the new image name for the server as a parameter
    :@param parameter: Parameter of the fix based on the type
    """
    query_workouts = ds_client.query(kind='cybergym-workout')
    query_workouts.add_filter('unit_id', '=', build_id)
    for workout in list(query_workouts.fetch()):
        for server in workout['servers']:
            if server['name'] == server_name:
                if type == "ssh-key":
                    print(f"Begin setting ssh key for {workout.key.name}")
                    server['sshkey'] = parameters
                    print(f"Completed setting ssh key for {workout.key.name}")
                elif type == "image-correction":
                    old_server_image = server['image']
                    print(f"Begin changing the image name in {workout.key.name} from {old_server_image} "
                          f"to {parameters}")
                    server['image'] = parameters
                    print(f"Completed image correction for {workout.key.name}")
                ds_client.put(workout)


if __name__ == "__main__":
    fix_server_in_unit()
