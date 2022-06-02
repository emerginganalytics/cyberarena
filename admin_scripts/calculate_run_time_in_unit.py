from google.cloud import datastore
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

__author__ = "Philip Huff"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Production"


# Parse command line arguments
parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
parser.add_argument("-u", "--unit", default=None, help="Unit ID in which to delete the server")

args = vars(parser.parse_args())

# Set up parameters
unit_id = args['unit']


def calculate_run_time_in_unit(unit_id):
    """
    Use this function to delete a server from each workout in a unit.
    """
    ds_client = datastore.Client()
    query_workouts = ds_client.query(kind='cybergym-workout')
    query_workouts.add_filter('unit_id', '=', unit_id)
    total_runtime = 0
    for workout in list(query_workouts.fetch()):
        runtime_seconds = workout.get('runtime_counter', 0)
        total_runtime += runtime_seconds
    print(f"Total runtime for unit {unit_id}: {total_runtime/3600} hours")



if __name__ == "__main__":
    if not unit_id:
        print("Error: Must supply a unit ID")
    else:
        calculate_run_time_in_unit(unit_id)
