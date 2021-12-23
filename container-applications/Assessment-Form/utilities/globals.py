from google.cloud import datastore, storage, runtimeconfig
from google.cloud import logging as g_logging

ds_client = datastore.Client()
runtimeconfig_client = runtimeconfig.Client()
myconfig = runtimeconfig_client.config('cybergym')
project = myconfig.get_variable('project').value.decode("utf-8")
dns_suffix = myconfig.get_variable('dns_suffix').value.decode("utf-8")
api_key = myconfig.get_variable('api_key').value.decode("utf-8")

auth_config = {
    'api_key': api_key,
    'auth_domain': str(project + ".firebaseapp.com"),
    'project_id': project
}