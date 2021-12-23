"""
This function is used on the landing page for the student in case they lock themselves out of their workout or
irreversibly damage any of their systems which would prevent them from continuing. The function deletes all of the
resources in a workout and then rebuilds everything based on the same specification.
"""
import time
from common.state_transition import state_transition
from common.globals import ds_client, BUILD_STATES, log_client, LOG_LEVELS, WORKOUT_TYPES
from common.delete_expired_workouts import DeletionManager
from common.build_workout import build_workout


def nuke_workout(workout_id):
    """
    :param workout_id: The ID of the workout specification in the Datastore
    :returns: None
    """
    g_logger = log_client.logger(str(workout_id))
    workout = ds_client.get(ds_client.key('cybergym-workout', workout_id))
    g_logger.log_text("Nuke Operation: Delete")
    state_transition(entity=workout, new_state=BUILD_STATES.NUKING)
    DeletionManager(deletion_type=DeletionManager.DeletionType.SPECIFIC, build_id=workout_id,
                    build_type=WORKOUT_TYPES.WORKOUT).run()
    time.sleep(60)

    g_logger.log_text("Nuke Operation: Rebuild")
    state_transition(entity=workout, new_state=BUILD_STATES.START)
    build_workout(workout_id)
    return
