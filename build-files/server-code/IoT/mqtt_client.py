#!/usr/bin/python3
"""
    Name: mqtt_client.py
    
    Created by: Andrew Bomberger
    
    For: UA Little Rock Cyber Arena
    
    About:  MQTT client class used for the Cyber Arena IOT workout.
            Designed with the idea of being run as a background
            service.
"""
import datetime
import json
import jwt
import logging
import paho.mqtt.client as mqtt
import re
import time
import threading
import yaml
from controller import SenseHatControls, Colors
from multiprocessing import Pipe, Process
from system_status import SystemInfo


with open('/usr/src/cyberarena-dev/config.yaml') as file:
    config = yaml.full_load(file)

# load project configs
ssl_private_key = config['certs']['ssl_private_key']
ssl_algorithm   = config['certs']['algorithm']
root_cert       = config['certs']['root_cert']
project_id      = config['gcp']['project_id']
zone            = config['gcp']['zone']
registry_id     = config['gcp']['registry_id']
device_id       = config['gcp']['device_id']

# initialize logger
logging.basicConfig(
        filename=config['log_file'],
        format="%(asctime)s [%(levelname)s] %(funcName)s: %(message)s",
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M')


class MQTT_Handler(object):
    """
        This class establishes connection to MQTT PubSub server based
        on settings listed in config.yaml and handles any commands 
        published to the {device_id}/commands/# topic.
    """
    def __init__(self, sense_thread, **kwargs):
        self._CLIENT_ID = f'projects/{project_id}/locations/{zone}/registries/{registry_id}/devices/{device_id}'
        self._MQTT_TELEMETRY_TOPIC = f'/devices/{device_id}/events'
        self._MQTT_CONFIG_TOPIC = f'/devices/{device_id}/config'
        self._MQTT_COMMANDS_TOPIC = f'/devices/{device_id}/commands/#'
        self.client = mqtt.Client(client_id=self._CLIENT_ID)
        self.sys_time = time.time()
        self.system_info = ''
        self.initialized = False

        # SenseHatControl variables
        self.prev_accel = 0
        # If sense_thread = True, thread exists but is not joined
        self.sense_thread = sense_thread

        # Run Class
        self.driver()

    def create_jwt(self):
        """
            returns string that is used for MQTT.Client password
        """
        cur_time = datetime.datetime.utcnow()
        token = {
            'iat': cur_time,
            'exp': cur_time + datetime.timedelta(minutes=60),
            'aud': project_id
        }
        with open(ssl_private_key, 'r') as f:
            private_key  = f.read()
        return jwt.encode(token, private_key, ssl_algorithm)

    def error_str(self, rc):
        message = f'{rc}: {mqtt.error_string(rc)}'
        logging.info(message)
        return str(message)

    def on_connect(self, client, userdata, flags, rc):
        """
            Handles connection events between
            the client and MQTT server
        """
        message = f'on_connect: {self.error_str(rc)}'
        logging.info(message)
        print(message)

        # adding the subscribe command here ensures that if a connection
        # is lost and restored, the subscription will be renewed
        client.subscribe(self._MQTT_COMMANDS_TOPIC, qos=1)

    def on_publish(self, client, userdata, mid):
        """
            Handles MQTT publish events
        """
        message = f'Publishing to topic; {userdata}'
        logging.info(message)

    def on_message(self, client, userdata, message):
        """
            Handles all incoming messages from the MQTT server
        """
        # Cleaning data and creating event log
        payload = str(message.payload)
        cleaned_msg = self.message_text(payload)
        log_message = f'Received message {payload} on topic {message.topic}'
        logging.info(log_message)

        # get SenseHat data
        current_time = time.time()
        system = self.system_info
        sense = SenseHatControls(init_time=current_time, sys_info=system)
        sensor_data = sense.get_all_sensor_data()

        # update system data
        self.sys_time = current_time
        self.system_info = sensor_data['system']

        # handle display based on msg value
        msg = cleaned_msg.upper()
        commands = {
            'BRAKE': sense.display_accel_brake,
            'CLEAR': sense.clear_display,
            'CRITICAL': sense.accel_critical,
            'GAS': sense.display_accel,
            'HEART': sense.display_heartrate,
            'HUMIDITY': sense.display_humidity,
            'PRESSURE': sense.display_pressure,
            'SNAKE': sense.snake,
            'TEMP': sense.display_temp,
            'UNLOCK': sense.display_combination,
        }
        # Make sure previous thread is complete before creating new one
        """
            We only want to join the thread if the publish call comes from outside of
            the initial mqtt connected publish requests
        """
        if self.sense_thread.is_alive():
            self.sense_thread.join()

        # Check for valid command
        if msg == 'SSN':
            sensor_data['sensor_data']['flag'] = sense.curious2
        elif msg in commands:
            if msg == 'CRITICAL':
                sensor_data['sensor_data']['flag'] = sense.accel_crit_msg
            # Heart is a special case that takes in int value to display
            if msg == 'HEART':
                data = [msg, sensor_data['sensor_data']['heart']]
            else:
                data = [msg, None]

            # Create threat for current cmd
            self.sense_thread = threading.Thread(
                target=SenseHatControls(
                    init_time=self.sys_time,
                    sys_info=self.system_info).process_thread_msg,
                args=(data,))
            self.sense_thread.start()
        # Command is possibly a Color request; No thread needed
        else:
            if msg in Colors:
                sense.display_color(msg)
                sensor_data['sensor_data']['color'] = msg
                if msg == 'GREEN':
                    sensor_data['sensor_data']['flag'] = sense.curious
            # Invalid cmd
            else:
                sensor_data = f'Invalid Command: {msg}'

        """if msg in commands:
            if msg == 'CRITICAL':
                sensor_data['sensor_data']['flag'] = sense.accel_crit_msg
            # Pass command to process 2 and free up this process
            if msg == 'HEART':
                print('HEART')
                #self.parent_pipe.send([msg, sense.heartrate])
            else:
                self.parent_pipe.send([msg])
        else:
            # Colors commands don't lock the process, no need to pass on to process 2
            if msg in Colors:
                if msg == 'GREEN':
                    sensor_data['sensor_data']['flag'] = sense.curious
                else:
                    sensor_data['sensor_data']['color'] = msg
                self.parent_pipe.send([msg])
            else:
                sensor_data = f'Invalid Command: {cleaned_msg}'"""

        # publish returned data
        return_data = json.dumps(sensor_data)
        client.publish(topic=self._MQTT_TELEMETRY_TOPIC, qos=1, payload=return_data)

    def message_text(self, orig):
        """strips GCP noise"""
        logging.info(f'matching message text: {orig}')
        ma = re.match(r'^b\'(.*)\'$', orig)

        if ma == None:
            return orig
        else:
            return ma.group(1)

    def driver(self):
        """
            Main server function. Controls client object
            and handles connections
        """
        print('init driver')
        self.initialized = False

        # JWT Authorization
        self.client.username_pw_set(
            username='unused',
            password=self.create_jwt()
        )
        regExp = re.compile('1')

        # declare how each client action should be handled
        self.client.on_connect = self.on_connect
        self.client.on_publish = self.on_publish
        self.client.on_message = self.on_message

        # connect to mqtt server
        self.client.tls_set(ca_certs=root_cert)
        self.client.connect(host='mqtt.googleapis.com', port=8883, keepalive=60)
        self.system_info = SystemInfo().get_all_info()
        SenseHatControls(init_time=self.sys_time, sys_info=self.system_info).connected()

        for i in range(3):
            print('Getting init sensor data')
            sensor_data = SenseHatControls(init_time=self.sys_time, sys_info=self.system_info).get_all_sensor_data()
            print(f'received: {sensor_data}')
            return_data = json.dumps(sensor_data)
            self.client.publish(topic=self._MQTT_TELEMETRY_TOPIC, qos=1, payload=return_data)

        # We want to run indefinitely. Note: this could lead to
        # indefinite looping to a non-existent host (if network is down)
        print('starting client_loop')
        self.initialized = True
        self.client.loop_forever(retry_first_connection=True)


if __name__ == '__main__':
    init_time = int(time.time())
    sys_info = ''
    data = [None, None]

    # Create Thread
    SENSE_THREAD = threading.Thread(target=SenseHatControls(init_time=init_time, sys_info=sys_info).process_thread_msg, args=(data, ))
    MQTT_Handler(sense_thread=SENSE_THREAD)

# [ eof ]
