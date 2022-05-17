from common.globals import ds_client, BUILD_STATES, project
from common.build_workout import build_workout
from common.state_transition import state_transition


def rebuild_workout(workout_id):
    """
    Builds a full workout
    :param workout_id: The workout_id to build
    """
    workout = ds_client.get(ds_client.key('cybergym-workout', workout_id))
    state_transition(entity=workout, new_state=BUILD_STATES.START)
    build_workout(workout_id)
    return

