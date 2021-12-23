import time
import calendar

from common.globals import ds_client, ordered_workout_build_states, ordered_arena_states, BUILD_STATES, LOG_LEVELS, log_client, \
    ds_safe_put


def state_transition(entity, new_state, existing_state=None):
    """
    Consistently changes a datastore entity with the necessary state checks.
    :param entity: A datastore entity
    :param new_state: The new state for the server
    :param existing_state: A check for the existing state of the server. This defaults to None.
    :return: Boolean on success. If the expected existing state is not the same as the actual, this returns False.
    """

    if 'state' not in entity:
        entity['state'] = None

    if existing_state and entity['state'] != existing_state:
        g_logger = log_client.logger(entity.key.name)
        g_logger.log_struct(
            {
                "message": "Error in state transition: Expected entity to be in {} state. Instead, it was in state {}".format(existing_state, entity['state'])
            }, severity=LOG_LEVELS.WARNING
        )
        # print(f"Error in state transition: Expected entity to be in {existing_state} state. Instead, it was in the state"
        #       f" {entity['state']}")
        return False
    ts = str(calendar.timegm(time.gmtime()))
    entity['state'] = new_state
    entity['state-timestamp'] = ts
    if new_state == BUILD_STATES.DELETED:
        entity['active'] = False
    elif new_state == BUILD_STATES.READY:
        entity['active'] = True
    g_logger = log_client.logger(entity.key.name)
    g_logger.log_text(str('State Transition {}: Transitioning to {} at {}'.format(entity.key.name, new_state, ts)))
    ds_safe_put(entity)
    return True


def check_ordered_workout_state(workout, ordered_state):
    """
    Workouts are built in a designated order. This function checks the state to determine if the workout is in a valid
    state to begin performing a function
    :param workout: A datastore cybergym-workout entity
    :param ordered_state: An ordered state to verify it has not already been performed for a given workout. For example,
    we would not want to attempt building a network again if it's already built.
    """
    if 'state' not in workout:
        workout['state'] = None
        ds_client.put(workout)
        return False

    if workout['state'] not in ordered_workout_build_states:
        return False

    if ordered_workout_build_states[workout['state']] <= ordered_workout_build_states[ordered_state]:
        return True
    else:
        return False


def check_ordered_arenas_state(unit, ordered_state):
    """
    Workouts are built in a designated order. This function checks the state to determine if the unit is in a valid
    state to begin performing a function
    :param unit: A datastore cybergym-unit entity
    :param ordered_state: An ordered state to verify it has not already been performed for a given unit. For example,
    we would not want to attempt building a network again if it's already built.
    """
    if 'state' not in unit:
        unit['state'] = None
        ds_client.put(unit)
        return False

    if unit['state'] not in ordered_arena_states:
        return False

    if ordered_arena_states[unit['state']] <= ordered_arena_states[ordered_state]:
        return True
    else:
        return False
