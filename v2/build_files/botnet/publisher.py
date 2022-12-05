import os
from google.cloud import pubsub_v1
from google.cloud import runtimeconfig

class Publisher:
    def __init__(self):
        runtimeconfig_client = runtimeconfig.Client()
        myconfig = runtimeconfig_client.config('cybergym')
        self.project = myconfig.get_variable('project').value.decode('utf-8')
        self.region = myconfig.get_variable('region').valud.decode('utf-8')
        self.zone = myconfig.get_variable('zone').value.decode('utf-8')
        self.dns_suffix = myconfig.get_variable('dns_suffix').value.decode('utf-8')

creds = ''
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = creds

publisher = pubsub_v1.PublisherClient()
topic_path = ''

data = 'Sending command now..'
data = data.encode('utf-8')

attributes = {
    "attack_args": "{\"option\": \"-T5\", \"target_machine\": \"harden-linux\", \"target_id\": \"cqkrolepzw\", \"target_build_type\": \"fixed_arena_class\", \"target_addr\": \"10.1.0.10\"}",
    "attack_id": "iwsibovpqj",
    "attack_module": "nmap",
    "build_id": "tynhzscvcp"
}



future = publisher.publish(topic_path, data, **attributes)
print(f'Published message id {future.result()}')
