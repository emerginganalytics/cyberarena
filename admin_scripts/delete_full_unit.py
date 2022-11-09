from common.globals import ds_client, BUILD_STATES, WORKOUT_TYPES
from common.delete_expired_workouts import DeletionManager
from common.state_transition import state_transition
from common.budget_management import BudgetManager
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter


# Parse command line arguments
parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
parser.add_argument("-u", "--unit", default=None, help="Unit to delete")
parser.add_argument("-d", "--debug", default=False, help="Whether to debug ")

args = vars(parser.parse_args())

# Set up parameters
unit_id = args.get('unit', None)
debug = args.get('debug', False)


def delete_unit(unit_id, delete_key=False, delete_immediately=False):
    """
    Deletes a full unit when it was created on accident
    :param unit_id: The unit_id to delete
    :param delete_key: Boolean on whether to delete the Datastore entity
    :param delete_immediately: Whether to delete immediately or create misfits and let the cloud function delete this.
    """
    bm = BudgetManager()
    query_workouts = ds_client.query(kind='cybergym-workout')
    query_workouts.add_filter('unit_id', '=', unit_id)
    for workout in list(query_workouts.fetch()):
        workout['misfit'] = True
        ds_client.put(workout)
    print("All workouts marked as misfits. Starting to process the delete workouts function")
    if bm.check_budget():
        DeletionManager(deletion_type=DeletionManager.DeletionType.MISFIT, debug=debug).run()
        print("Completed deleting workouts")
    else:
        print("Cannot delete misfits. Budget exceeded variable is set for this project.")

if __name__ == "__main__":
    if not unit_id:
        unit_id = str(input(f"What unit ID do you wish to delete?: "))
    delete_unit(unit_id)
    while True:
        response = str(input("Do you wish to delete any additional units (y/N)?"))
        if not response or str.upper(response) == "N":
            break
        else:
            unit_id = str(input(f"What unit ID do you wish to delete?: "))
            delete_unit(unit_id)
