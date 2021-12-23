import calendar
import time
from common.globals import ds_client, BUILD_STATES, PUBSUB_TOPICS, project, WORKOUT_TYPES
from common.delete_expired_workouts import DeletionManager
from common.state_transition import state_transition
from google.cloud import pubsub_v1


def delete_all_active_units(keep_data=False):
    """
    This will delete ALL active units and should be used only during special functions when no other activity is
    occurring
    :param keep_data: Specifies whether to mark the active workouts as misfits or change the expiration time to now.
    """
    query_workouts = ds_client.query(kind='cybergym-workout')
    query_workouts.add_filter('active', '=', True)
    for workout in list(query_workouts.fetch()):
        workout_project = workout.get('build_project_location', project)
        if workout_project == project:
            if 'state' in workout and workout['state'] != BUILD_STATES.DELETED:
                if keep_data:
                    workout['expiration'] = 0
                else:
                    workout['misfit'] = True
                ds_client.put(workout)
    print("All active workouts have been processed. Starting to process the delete workouts function")
    if keep_data:
        DeletionManager(deletion_type=DeletionManager.DeletionType.EXPIRED).run()
    else:
        DeletionManager(deletion_type=DeletionManager.DeletionType.MISFIT).run()
    print("Sent commands to delete workouts and arenas")
