from google.cloud import datastore, runtimeconfig
import requests

# Global Server Variables
ds_client = datastore.Client()
runtimeconfig_client = runtimeconfig.Client()
myconfig = runtimeconfig_client.config('cybergym')
project = myconfig.get_variable('project').value.decode('utf-8')
dns_suffix = myconfig.get_variable('dns_suffix').value.decode('utf-8')
main_app_url = myconfig.get_variable('main_app_url').value.decode('utf-8')


def publish_status(workout_id, workout_key):
    # Sends completion status for individual question
    # Primarily used by auto complete workouts
    url = f'{main_app_url}/complete'
    status = {
        "workout_id": workout_id,
        "token": workout_key,
    }

    publish = requests.post(url, json=status)
    print(f'[*] POSTING to {url} ...')
    print(publish)
