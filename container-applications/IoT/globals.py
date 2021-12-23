from google.cloud import datastore, runtimeconfig
import requests

# Google Cloud Config
ds_client = datastore.Client()
runtimeconfig_client = runtimeconfig.Client()
myconfig = runtimeconfig_client.config('cybergym')
project = myconfig.get_variable('project').value.decode("utf-8")
dns_suffix = myconfig.get_variable('dns_suffix').value.decode("utf-8")


def publish_status(workout_id, workout_key):
    URL = f'https://buildthewarrior{dns_suffix}/complete'

    status = {
        "workout_id": workout_id,
        "token": workout_key,
    }

    publish = requests.post(URL, json=status)
    print(f'[*] POSTING to {URL} ...')
    print(publish)
