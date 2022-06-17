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
        self.kind = 'cyberarena-c_and_c'          # NA
        self.spec_kind = 'cyberarena-attack-spec' # Kind to load attack templates
        self.attack_kind = 'cyberarena-attack'    # Kind to send requested attacks to
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
        for template in spec_str['attack']:
            if template['id'] == attack_id:
                return template
        return f'Invalid value for attack_id: {attack_id}'

    # Datastore methods
    def create_datastore_entry(self, unit_id, data):
        attack_ds = ds_client.get(self.kind)

        # Building the attack object to insert into the datastore
        attack_ds['attack_id'] = 'TBD'               # TODO: Figure out what the key needs to look like
        attack_ds['unit_id'] = unit_id               # Unit that is initializing
        attack_ds['mode'] = data['mode']             # Either inject or attack
        attack_ds['state'] = self.States.WORKING     # Current state of attack
        attack_ds['time'] = datetime.datetime.now()  # Time of attack initiation
        attack_ds['network'] = data['network']       # Network to inject attack/vuln on
        attack_ds['args'] = data['args']             # Script specific arguments
        attack_ds['scope'] = data['scope']           # Network is either unit wide or a single workout
        # Update datastore obj
        ds_client.put(attack_ds)

    def get_all_datastore_entries(self, unit_id):
        """Returns all attack entries for specific unit"""
        attack_query = ds_client.query(kind=self.kind)
        attack_query.add_filter('unit_id', '=', unit_id)
        attack_list = list(attack_query.fetch())
        return attack_list

    def process_form(self, form_data):
        """Handles forms for attack template build requests"""
        attack_id = form_data.get('attack_id')
        attack_spec = self.get_spec_by_id(attack_id)
        mode = attack_spec.get('mode', None)
        unit_id = form_data.get('unit_id', None)
        if 'target_unit' in form_data:
            network = form_data['target_unit']
            scope = 'unit'
        elif 'target_workout' in form_data:
            network = form_data['target_workout']
            scope = 'workout'
        args = []

        ignore_list = []
        if unit_id:
            ignore_list.append(unit_id)

        return {'unit_id': unit_id, 'mode': mode, 'network': network, 'scope': scope, 'args': args}

# [ eof ]
