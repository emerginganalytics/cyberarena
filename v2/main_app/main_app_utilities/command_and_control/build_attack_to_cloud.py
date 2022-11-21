from google.cloud import logging_v2
from datetime import datetime, timezone
from marshmallow import ValidationError
import random
import string

from main_app_utilities.command_and_control.attack_schema import AttackSchema
from main_app_utilities.gcp.cloud_env import CloudEnv
from main_app_utilities.gcp.bucket_manager import BucketManager
from main_app_utilities.gcp.datastore_manager import DataStoreManager
from main_app_utilities.gcp.pubsub_manager import PubSubManager
from main_app_utilities.globals import BuildConstants, DatastoreKeyTypes, PubSub, get_current_timestamp_utc

__author__ = "Andrew Bomberger"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Andrew Bomberger"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class AttackSpecToCloud:
    """
    Prepares the build of workouts based on a YAML specification by storing the information in the
    cloud datastore.
    :@param attack_spec: The specification for building the Inject or Weakness
    :@param debug: Whether to publish to cloud functions or debug the build operations.
    """
    def __init__(self, cyber_arena_attack, debug=False):
        self.env = CloudEnv()
        log_client = logging_v2.Client()
        log_client.setup_logging()
        self.cyber_arena_attack = cyber_arena_attack
        self.datastore_manager = DataStoreManager()
        self.debug = debug
        self.parent_build_type = self.cyber_arena_attack.get('parent_build_type', BuildConstants.BuildType.FIXED_ARENA_CLASS.value)
        self.build_type = self.cyber_arena_attack.get('build_type', self.parent_build_type)
        self.build_id = self.cyber_arena_attack['args'].get('target_id')
        if 'mode' not in self.cyber_arena_attack:
            raise ValidationError(f'No value for mode given in AttackSpecToCloud')
        self.cyber_arena_attack['creation_timestamp'] = str(datetime.fromtimestamp(get_current_timestamp_utc()))
        self.pubsub_manager = PubSubManager(topic=PubSub.Topics.CYBER_ARENA.value)
        self.mode = self.cyber_arena_attack['mode']

        if self.mode == BuildConstants.BuildType.FIXED_ARENA_ATTACK.value:
            self.action = PubSub.BuildActions.CYBER_ARENA_ATTACK.value
            self.attack_id = ''.join(random.choice(string.ascii_lowercase) for j in range(10))
            self.cyber_arena_attack['id'] = self.attack_id
            self.args = self.cyber_arena_attack['args']
            self.cyber_arena_attack = AttackSchema().load(self.cyber_arena_attack)
            self.cyber_arena_attack['logs'] = []
            self.cyber_arena_attack['topics'] = {
                'commands': f'{self.cyber_arena_attack["parent_id"]}-agency',
                'telemetry': str(PubSub.Topics.AGENT_TELEMETRY.value)
            }
            self.datastore_manager = DataStoreManager(key_type=DatastoreKeyTypes.CYBERARENA_ATTACK.value,
                                                      key_id=self.attack_id)
        else:
            raise ValidationError(f'Unrecognized value ({self.mode}) for BuildType in BuildAttackToCloud')

    def commit(self):
        """Sends PubSub request for requested inject build"""
        self.datastore_manager.put(self.cyber_arena_attack)
        if not self.debug:
            self.pubsub_manager.msg(handler=str(PubSub.Handlers.AGENCY.value), action=str(self.action),
                                    attack_id=self.attack_id, build_id=str(self.build_id),
                                    build_type=str(self.build_type))

# [ eof ]
