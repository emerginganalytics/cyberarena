import click
import calendar
import time
from datetime import datetime
from datetime import timedelta
from common.globals import ds_client, BUILD_STATES
from common.nuke_workout import nuke_workout
from common.state_transition import state_transition


def get_current_expiration_dates():
    """
    Reports the current expiration dates by unit and instructor name
    @return: None
    """
    workouts = ds_client.query(kind='cybergym-workout')
    workouts.add_filter('active', '=', True)
    expiration_report = {}
    for workout in list(workouts.fetch()):
        if workout['state'] != BUILD_STATES.DELETED and 'expiration' in workout:
            unit = workout['unit_id']
            if unit in expiration_report:
                expiration_report[unit]['count'] += 1
            else:
                start_ts = datetime.fromtimestamp(float(workout['timestamp']))
                expiry = (start_ts + timedelta(days=int(workout['expiration']))).isoformat()
                expiration_report[unit] = {
                    'instructor': workout['user_email'],
                    'expiration': expiry,
                    'type': workout['type'],
                    'count': 1
                }
    for unit in expiration_report:
        report_data = expiration_report[unit]
        print(f"{report_data['instructor']} has {report_data['count']} workouts in unit {unit} of type {report_data['type']} expiring {report_data['expiration']}")


@click.command()
@click.argument('query_type')
def query_workouts(query_type):
    """
    Provides back report data on a Cyber Gym project
    :param query_type: The type of query to execute
    """
    if query_type == "expiration":
        get_current_expiration_dates()


if __name__ == "__main__":
    query_workouts()