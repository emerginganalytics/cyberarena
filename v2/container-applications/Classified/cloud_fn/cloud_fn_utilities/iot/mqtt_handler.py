import json
import time
import paho.mqtt.client as paho
from paho import mqtt

from cloud_fn_utilities.gcp.datastore_manager import DataStoreManager
from cloud_fn_utilities.globals import DatastoreKeyTypes, PubSub
from cloud_fn_utilities.gcp.pubsub_manager import PubSubManager
from cloud_fn_utilities.iot.exceptions import InvalidTopic, MissingAttributes, MaxAttemptsExceeded


class MqttHandler:
    _MAX_ATTEMPTS = 100
    _HOST = '9b87fa604e9a481a94f6523d165f5aeb.s1.eu.hivemq.cloud'
    _PORT = 8883

    def __init__(self, device_id):
        self.device_id = device_id
        self.topic = f'{PubSub.IotTopics.GENERAL.value}{self.device_id}'
        self.user = 'cloud-fn-proc'
        self.password = '21eRsPsrfrCcVgJP'
        self.client = paho.Client(client_id=self.device_id, userdata=None, protocol=paho.MQTTv5)
        self.pubsub_manager = PubSubManager(PubSub.Topics.IOT.value)

        # Connect local methods with Paho MQTT class methods
        self._setup()

    def poll(self):
        topic = f'{self.topic}/telemetry'

        # Connect to the HiveMQ broker
        self.client.connect(self._HOST, self._PORT)

        # Subscribe to the topic
        self.client.subscribe(topic)

        # Keep the Cloud Function running indefinitely
        print('Starting loop')
        self.client.loop_forever(retry_first_connection=True)

    def msg(self, msg):
        """Publishes message to <topic>/<device_id>/control"""
        topic = f'{self.topic}/control'
        payload = json.dumps(msg)

        # Connect to the HiveMQ broker
        self.client.connect(self._HOST, self._PORT, 60)
        self.client.loop_start()

        # Wait for the client to establish a connection
        attempts = 0
        while not self.client.is_connected() and attempts < self._MAX_ATTEMPTS:
            attempts += 1
            time.sleep(0.1)
        if attempts >= self._MAX_ATTEMPTS and not self.client.is_connected():
            raise MaxAttemptsExceeded(f'Timeout during publish attempt; Could not connect to broker ...')

        # Publish message
        event = self.client.publish(topic=topic, payload=payload, qos=1)
        event.wait_for_publish()

        # Disconnect client and stop the loop
        self.client.loop_stop()
        self.client.disconnect()

    def _setup(self):
        # Attach custom functions to Client event functions
        self.client.on_message = self._handle_message
        self.client.on_connect = self._on_connect
        self.client.on_subscribe = self._on_subscribe
        self.client.on_publish = self._on_publish

        # Setup
        self.client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
        self.client.username_pw_set(self.user, self.password)

    def _process_message(self, msg):
        """Parses out HiveMQ payload object and redirects messages to appropriate GCP PubSub topic"""
        topic = msg.topic
        message = json.loads(msg.payload.decode())
        device_id = message.get('device_id', None)
        if not device_id:
            raise MissingAttributes(f'Missing device_id on response to {topic}')

        parent = HiveMqTopics.parent(topic)
        payload = json.dumps({
            'topic': parent,
            'data': message
        })
        if parent == PubSub.IotTopics.GENERAL:
            self.pubsub_manager.msg(
                action=str(PubSub.IotActions.CONTROL.value), device_id=str(self.device_id),
                payload=payload
            )
        elif parent == PubSub.IotTopics.ELECTRIC:
            pass

    def _handle_message(self, client, userdata, msg):
        # Handle the received message here
        print("Received message: Topic={}, Payload={}".format(msg.topic, msg.payload.decode()))
        self.client.disconnect()
        self._process_message(msg)

    def _error_str(self, rc):
        message = f'{rc}: {paho.error_string(rc)}'
        return str(message)

    def _on_connect(self, client, userdata, flags, reason, properties=None):
        message = f'on_connect: {self._error_str(reason)}'
        print(message)
        return str(message)

    def _on_subscribe(self, client, userdata, mid, granted_qos, properties=None):
        print("Subscribed: " + str(mid) + " " + str(granted_qos))

    def _on_publish(self, client, userdata, mid):
        print("mid: " + str(mid))
        pass

    def on_log(self, mqttc, obj, level, string):
        print(string)
        

class HiveMqTopics:
    """
    Takes input_topic and extracts the parent topic to help with task delegation.
    """
    TOPICS = PubSub.IotTopics

    @classmethod
    def parent(cls, input_topic):
        for topic in cls.TOPICS:
            if cls.is_child(input_topic, topic.value):
                return topic
        raise InvalidTopic(f'Unrecognized topic: {input_topic}')

    @classmethod
    def is_child(cls, child_topic, parent_topic):
        parent_topic_parts = parent_topic.split('/')
        child_topic_parts = child_topic.split('/')

        # Ensure the child topic has more parts than the parent topic
        if len(child_topic_parts) <= len(parent_topic_parts):
            return False

        # Check if each part of the parent topic matches the corresponding part of the child topic
        for i in range(len(parent_topic_parts)):
            if parent_topic_parts[i] != '' and parent_topic_parts[i] != child_topic_parts[i]:
                return False

        return True

# [ eof ]
