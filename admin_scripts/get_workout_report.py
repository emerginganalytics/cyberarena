import csv
from datetime import datetime, timezone, timedelta
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from common.globals import ds_client, BUILD_STATES, WORKOUT_TYPES
from google.cloud import datastore
from common.delete_expired_workouts import DeletionManager
from common.state_transition import state_transition
from common.budget_management import BudgetManager

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
parser.add_argument("-b", "--begin_date", required=False, default=None, help="Begin date in ISO 8601 format with no "
                                                                             "timestamp")
parser.add_argument("-e", "--end_date", required=False, default=None, help="End date in ISO 8601 format with no "
                                                                           "timestamp")

args = vars(parser.parse_args())

begin_date = args.get('begin_date', None)
end_date = args.get('end_date', None)


def get_workout_report(begin_date, end_date):
    """
    Gets a report on student workouts for a given timespan
    """
    if begin_date:
        begin_ts = int(datetime.fromisoformat(begin_date).timestamp())
    else:
        begin_ts = int((datetime.now() - timedelta(days=365)).timestamp())

    if end_date:
        end_ts = int(datetime.fromisoformat(end_date).timestamp())
    else:
        end_ts = int(datetime.now().timestamp())
    query_workouts = ds_client.query(kind='cybergym-workout')
    query_workouts.add_filter('timestamp', '>', str(begin_ts))

    rows = []
    for workout in list(query_workouts.fetch()):
        workout_creation_ts = int(workout['timestamp'])
        if workout_creation_ts > begin_ts and workout_creation_ts < end_ts:
            creation_time = datetime.fromtimestamp(workout_creation_ts).isoformat()
            if type(workout.get('student_name', None)) == datastore.Entity:
                student_name = workout['student_name']['student_name']
            else:
                student_name = workout.get('student_name', None)
            rows.append([
                workout.key.name,
                creation_time,
                workout.get('user_email', None),
                workout.get('expiration', None),
                workout.get('type', None),
                workout.get('build_type', None),
                workout.get('unit_id', None),
                workout.get('hourly_cost', None),
                workout.get('runtime_counter', None),
                workout.get('student_email', None),
                student_name
            ])

    header = ['Workout ID', 'Date Created', 'Instructor Email', 'Days to make available', 'Workout Name',
              'Workout Type', 'Unit', 'Cost Per Hour', 'Seconds run', 'Student Email', 'Student Name']
    with open('reports/workout_report.csv', 'w', newline='', encoding='UTF8') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)


if __name__ == "__main__":
    get_workout_report(begin_date, end_date)
