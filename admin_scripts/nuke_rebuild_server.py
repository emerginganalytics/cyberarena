from common.globals import project, zone, dnszone, ds_client, compute, SERVER_STATES, SERVER_ACTIONS, PUBSUB_TOPICS
from google.cloud import pubsub_v1
import time

def nuke_rebuild_server(server_name):
    pubsub_topic = PUBSUB_TOPICS.MANAGE_SERVER
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project, pubsub_topic)
    future = publisher.publish(topic_path, data=b'Server Delete', server_name=server_name,
                               action=SERVER_ACTIONS.DELETE)
    print(future.result())
    time.sleep(30)
    pubsub_topic = PUBSUB_TOPICS.MANAGE_SERVER
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project, pubsub_topic)
    future = publisher.publish(topic_path, data=b'Server Build', server_name=server_name, action=SERVER_ACTIONS.BUILD)