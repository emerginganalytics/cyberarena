"""
Used for injecting vulnerabilities into target workouts or units
"""
import datetime
from google.cloud import datastore
from utilities.globals import ds_client, project, log_client, LOG_LEVELS
from utilities.yaml_functions import YamlFunctions

__author__ = "Andrew Bomberger"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Andrew Bomberger"]
__license__ = "MIT"
__version__ = "0.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Development"


class VulnManager(object):
    # TODO: This class acts as a medium between the teacher app and cloud functions
    def __init__(self):
        self.kind = 'cyberarena-c_and_c'
        self.spec_name = 'attack'

    class States:
        """
        TODO: Current state values are not permanent. Will be finalized once more of the framework is
              in place
        """
        COMPLETE = 'COMPLETE'
        FAILED = 'FAILED'
        READY = 'READY'
        RUNNING = 'RUNNING'
        WORKING = 'WORKING'

    @property
    def load_yaml_str(self):
        return YamlFunctions().parse_yaml(self.spec_name)

    def get_spec_by_id(self, attack_id):
        spec_str = self.load_yaml_str
        for a_id in spec_str['attack']:
            if a_id['id'] == attack_id:
                return a_id
        return f'Invalid value for attack_id {attack_id}'

    # Datastore methods
    def create_datastore_entry(self, unit_id, data):
        attack_ds = ds_client.get(self.kind)

        # Building the attack object to insert into the datastore
        attack_ds['unit_id'] = unit_id               # Unit that is initializing
        attack_ds['mode'] = data['mode']             # Either inject or attack
        attack_ds['status'] = self.States.WORKING    # Current state of attack
        attack_ds['time'] = datetime.datetime.now()  # Time of attack initiation
        attack_ds['network'] = 'TBD'                 # Network to inject attack/vuln on
        attack_ds['args'] = data['args']             # Script specific arguments

        # Update datastore obj
        ds_client.put(attack_ds)

    def get_all_datastore_entries(self, unit_id):
        """Returns all attack entries for specific unit"""
        attack_query = ds_client.query(self.kind)
        attack_query.filter('unit_id', '==', unit_id)
        attack_list = list(attack_query.fetch())
        return attack_list


# [ eof ]
