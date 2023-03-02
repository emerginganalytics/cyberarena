
# reset for broken workouts

from google.cloud import datastore

__Author__ = 'Bill'
__Version__ = '2.0'
__Status__ = 'Testing'
__Date__ = '2022-03-01'
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff"]
__license__ = "MIT"
__maintainer__ = "Philip Huff"


# function to fix broken workouts
def fix_broken():
    client = datastore.Client()  # connect to datastore
    workout_id = input('enter key: ')  # get key
    key = client.key('v2-workout', workout_id)  # create key
    state = client.get(key)['state']  # get state
    if state == 62:  # if state is broken
        state = client.get(key)  # get state
        state.update(  # update state
            {
                "state": 53,  # set state to ready
            }
        )
        client.put(state)  # update datastore entity with new state


fix_broken()  # execute function

"""
class FixedArenaClassStates(Enum):
    START = 0
    BUILDING_ASSESSMENT = 1
    BUILDING_NETWORKS = 2
    COMPLETED_NETWORKS = 3
    BUILDING_SERVERS = 4
    COMPLETED_SERVERS = 5
    BUILDING_FIREWALL = 6
    COMPLETED_FIREWALL = 7
    BUILDING_ROUTES = 8
    COMPLETED_ROUTES = 9
    BUILDING_FIREWALL_RULES = 10
    COMPLETED_FIREWALL_RULES = 11
    BUILDING_STUDENT_ENTRY = 12
    COMPLETED_STUDENT_ENTRY = 13
    GUACAMOLE_SERVER_LOAD_TIMEOUT = 28
    RUNNING = 50
    STOPPING = 51
    STARTING = 52
    READY = 53
    EXPIRED = 60
    MISFIT = 61
    BROKEN = 62
    DELETING_SERVERS = 70
    COMPLETED_DELETING_SERVERS = 71
    DELETED = 72
"""
