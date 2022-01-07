"""
The competition arena requires a build in which all student servers reside in the same network. These classes
support the cloud build of the competition arena according to the specification.
"""

import time
import random
import string
from googleapiclient.errors import HttpError
from google.cloud import pubsub_v1

from common.globals import ds_client, log_client, LOG_LEVELS, project, compute, region, zone, workout_globals, \
    BUILD_STATES, cloud_log, LogIDs, PUBSUB_TOPICS, SERVER_ACTIONS
from common.dns_functions import add_dns_record
from common.stop_compute import stop_workout, stop_arena
from common.networking_functions import create_network, create_route, create_firewall_rules
from common.state_transition import state_transition, check_ordered_arenas_state

__author__ = "Philip Huff"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Production"


class CompetitionArena:
    STUDENT_NETWORK_NAME = 'student-network'
    STUDENT_NETWORK_SUBNET = '10.1.0.0/16'

    def __init__(self, unit_id):
        self.unit_id = unit_id

    def build(self):
        key = ds_client.key('cybergym-unit', self.unit_id)
        unit = ds_client.get(key)
        # This can sometimes happen when debugging a Unit ID and the Datastore record no longer exists.
        arena = unit['arena']
        if not arena:
            cloud_log(self.unit_id, f"Build operation failed. No unit {self.unit_id} exists in the data store",
                      LOG_LEVELS.ERROR)
            raise LookupError

        if 'state' not in unit or not unit['state']:
            state_transition(entity=unit, new_state=BUILD_STATES.START)

        # STATE: BUILDING_STUDENT_NETWORKS
        if check_ordered_arenas_state(unit, BUILD_STATES.BUILDING_ARENA_STUDENT_NETWORKS):
            cloud_log(self.unit_id, f"Creating student networks for arena {self.unit_id}", LOG_LEVELS.INFO)
            student_network = [{
                    'name': self.STUDENT_NETWORK_NAME,
                    'subnets': [{'name': f'{self.unit_id}-{self.STUDENT_NETWORK_NAME}-default',
                                 'ip_subnet': self.STUDENT_NETWORK_SUBNET}]
                }]
            try:
                create_network(networks=student_network, build_id=self.unit_id)
            except HttpError as err:
                if err.resp.status not in [409]:
                    cloud_log(self.unit_id, f"Error when trying to create the student network for "
                                            f"the arena {self.unit_id}", LOG_LEVELS.ERROR)
                    raise

        # STATE: BUILDING_ARENA_NETWORKS
        if check_ordered_arenas_state(unit, BUILD_STATES.BUILDING_ARENA_NETWORKS):
            state_transition(entity=unit, new_state=BUILD_STATES.BUILDING_ARENA_NETWORKS)
            if arena['networks']:
                cloud_log(self.unit_id, f"Creating additional arena networks for arena {self.unit_id}", LOG_LEVELS.INFO)
                create_network(networks=arena['networks'], build_id=self.unit_id)
            state_transition(entity=unit, new_state=BUILD_STATES.COMPLETED_ARENA_NETWORKS)

        # STATE: BUILDING_ARENA_SERVERS
        if check_ordered_arenas_state(unit, BUILD_STATES.BUILDING_ARENA_SERVERS):
            state_transition(entity=unit, new_state=BUILD_STATES.BUILDING_ARENA_SERVERS)
            cloud_log(self.unit_id, f"Creating additional servers for arena {self.unit_id}", LOG_LEVELS.INFO)
            server_list = list(
                ds_client.query(kind='cybergym-server').add_filter('workout', '=', self.unit_id).fetch())
            for server in server_list:
                server_name = server['name']
                cloud_log(self.unit_id, f"Sending pubsub message to build {server_name}", LOG_LEVELS.INFO)
                pubsub_topic = PUBSUB_TOPICS.MANAGE_SERVER
                publisher = pubsub_v1.PublisherClient()
                topic_path = publisher.topic_path(project, pubsub_topic)
                publisher.publish(topic_path, data=b'Server Build', server_name=server_name,
                                  action=SERVER_ACTIONS.BUILD)
            state_transition(entity=unit, new_state=BUILD_STATES.COMPLETED_ARENA_SERVERS)

        # STATE: BUILDING_ROUTES
        if check_ordered_arenas_state(unit, BUILD_STATES.BUILDING_ROUTES):
            state_transition(entity=unit, new_state=BUILD_STATES.BUILDING_ROUTES)
            cloud_log(self.unit_id, f"Creating network routes and firewall rules for arena {self.unit_id}",
                      LOG_LEVELS.INFO)
            if 'routes' in arena and arena['routes']:
                for route in arena['routes']:
                    r = {"name": f"{self.unit_id}-{route['name']}",
                         "network": f"{self.unit_id}-{route['network']}",
                         "destRange": route['dest_range'],
                         "nextHopInstance": f"{self.unit_id}-{route['next_hop_instance']}"}
                    create_route(route)
            state_transition(entity=unit, new_state=BUILD_STATES.COMPLETED_ROUTES)

        # STATE: BUILDING_FIREWALL
        if check_ordered_arenas_state(unit, BUILD_STATES.BUILDING_FIREWALL):
            state_transition(entity=unit, new_state=BUILD_STATES.BUILDING_FIREWALL)
            firewall_rules = []
            for rule in arena['firewall_rules']:
                if 'network' not in rule:
                    rule['network'] = self.STUDENT_NETWORK_NAME
                firewall_rules.append({"name": f"{self.unit_id}-{rule['name']}",
                                       "network": f"{self.unit_id}-{rule['network']}",
                                       "targetTags": rule['target_tags'],
                                       "protocol": rule['protocol'],
                                       "ports": rule['ports'],
                                       "sourceRanges": rule['source_ranges']})

            # Create the default rules to allow traffic between student networks.
            firewall_rules.append({"name": f"{self.unit_id}-allow-all-internal",
                                   "network": f"{self.unit_id}-{self.STUDENT_NETWORK_NAME}",
                                   "targetTags": [],
                                   "protocol": 'tcp',
                                   "ports": ['tcp/any', 'udp/any', 'icmp/any'],
                                   "sourceRanges": [self.STUDENT_NETWORK_SUBNET]})

            create_firewall_rules(firewall_rules)
            state_transition(entity=unit, new_state=BUILD_STATES.COMPLETED_FIREWALL)
