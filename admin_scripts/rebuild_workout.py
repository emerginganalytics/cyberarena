import time
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

from common.globals import ds_client, BUILD_STATES, project
from common.build_workout import build_workout
from common.state_transition import state_transition
from common.budget_management import BudgetManager
from common.delete_expired_workouts import DeletionManager

# Parse command line arguments
parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
parser.add_argument("-w", "--workout_id", default=None, help="Workout ID to rebuild")

args = vars(parser.parse_args())

# Set up parameters
workout_id = args.get('workout_id')


def rebuild_workout(workout_id):
    """
    Deletes and then builds a full workout
    :param workout_id: The workout_id to build
    """
    bm = BudgetManager()
    if bm.check_budget():
        DeletionManager()
        DeletionManager(deletion_type=DeletionManager.DeletionType.SPECIFIC, build_id=workout_id).run()
        print("Completed deleting workouts")
    else:
        print("Cannot delete misfits. Budget exceeded variable is set for this project.")
        return
    workout = ds_client.get(ds_client.key('cybergym-workout', workout_id))
    state_transition(entity=workout, new_state=BUILD_STATES.START)
    # This will allow the resources to delete before recreating.
    time.sleep(30)
    build_workout(workout_id, debug=True)
    return


if __name__ == "__main__":
    rebuild_workout(workout_id)
