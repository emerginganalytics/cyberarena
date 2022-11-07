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

creds = '/home/walker/Downloads/ualr-cybersecurity-38b2dd265fa9.json'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = creds

publisher = pubsub_v1.PublisherClient()
topic_path = 'projects/ualr-cybersecurity/topics/test'

data = 'Sending command now..'
data = data.encode('utf-8')

attributes = {
    'id':'nmap',
    'rhost':'127.0.0.1'
}



future = publisher.publish(topic_path, data, **attributes)
print(f'Published message id {future.result()}')
