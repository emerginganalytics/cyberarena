from google.cloud import pubsub

project_id = "ualr-cybersecurity"
topic_name = "del-workout"

publisher = pubsub.PublisherClient()
# The `topic_path` method creates a fully qualified identifier
# in the form `projects/{project_id}/topics/{topic_name}`
topic_path = publisher.topic_path(project_id, topic_name)

for n in range(1, 5):
    data = u'Message number {}'.format(n)

    # Data must be a bytestring
    data = data.encode('utf-8')

    # When you publish a message, the client returns a future.
    future = publisher.publish(topic_path, data=data)
    print(future.result())

print('Published messages.')
