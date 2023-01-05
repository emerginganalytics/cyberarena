from google.cloud import pubsub_v1
from google.cloud import runtimeconfig
import os
import json



class PubSubManager:
    def __init__(self):
        creds = ''
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = creds
        runtimeconfig_client = runtimeconfig.Client()
        myconfig = runtimeconfig_client.config('cybergym')
        self.project = myconfig.get_variable('project').value.decode("utf-8")
        self.region = myconfig.get_variable('region').value.decode("utf-8")
        self.zone = myconfig.get_variable('zone').value.decode("utf-8")
        self.topic = 'test'
        self.publisher = pubsub_v1.PublisherClient()
        self.topic_path = self.publisher.topic_path(self.project, self.topic)

    def msg(self, output):
        print(self.topic_path, self.project)
        future = self.publisher.publish(self.topic_path, data=output)
        print(f'Published message id {future.result()}')
