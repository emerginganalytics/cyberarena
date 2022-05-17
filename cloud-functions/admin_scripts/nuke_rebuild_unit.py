from common.globals import ds_client, BUILD_STATES, project
from common.nuke_workout import nuke_workout
from common.state_transition import state_transition


def nuke_rebuild_unit(unit_id):
    """
    Nukes a full unit. This can be helpful, for example, if you've run out of quota
    :param unit_id: The unit_id to delete
    :param delete_key: Boolean on whether to delete the Datastore entity
    """
    query_workouts = ds_client.query(kind='cybergym-workout')
    query_workouts.add_filter('unit_id', '=', unit_id)
    for workout in list(query_workouts.fetch()):
        workout_project = workout.get('build_project_location', project)
        if workout_project == project:
            print(f"Begin nuking and rebuilding workout {workout.key.name}")
            nuke_workout(workout.key.name)
            print(f"Completed nuking and rebuilding workout {workout.key.name}")


"""
if __name__ == "__main__":
    units = ['occahzxtnr', 'qinajihcjv']
    for unit in units:
        nuke_rebuild_unit(unit)
"""