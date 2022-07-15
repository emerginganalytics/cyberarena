from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

from common.globals import ds_client, BUILD_STATES, project
from common.build_workout import build_workout
from common.state_transition import state_transition

# Parse command line arguments
parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
parser.add_argument("-w", "--workout_id", default=None, help="Workout ID to rebuild")

args = vars(parser.parse_args())

# Set up parameters
workout_id = args.get('workout_id')


def rebuild_workout(workout_id):
    """
    Builds a full workout
    :param workout_id: The workout_id to build
    """
    workout = ds_client.get(ds_client.key('cybergym-workout', workout_id))
    state_transition(entity=workout, new_state=BUILD_STATES.START)
    build_workout(workout_id)
    return


if __name__ == "__main__":
    rebuild_workout(workout_id)
