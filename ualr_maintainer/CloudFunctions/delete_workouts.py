import googleapiclient.discovery
import google.cloud.logging as cloud_logging
from datetime import datetime, timedelta, date
from google.cloud import datastore 

cloud_client = cloud_logging.Client()
cloud_logger = cloud_client.logger('cloudfunctions.googleapis%2Fcloud-functions')
ds_client = datastore.Client()


def get_log_entries(any_function_name,limit=50):
    """
    Cloud Function that display log entries from Cloud Functions.
    Args:
        any_function_name: the fucntion log you want
        limit: max number of logs
    Returns:
        The logs for that function
    """
    all_entries = cloud_logger.list_entries(page_size=limit)
    entries = next(all_entries.pages)
    return entries


def get_workouts_to_delete():
    workouts = ds_client.query(kind='workout_resources_track')
    workouts_list = [ x for x in workouts if datetime.strptime(x['creation_data'],'%Y-%m-%dT%H:%M:%S')-datetime.now() > timedelta(days=x['duration'])]
    return workouts_list


def delete_old_workouts():
    old_workouts = get_workouts_to_delete()
    
