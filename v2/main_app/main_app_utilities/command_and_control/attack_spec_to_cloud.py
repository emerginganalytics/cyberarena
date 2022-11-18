from marshmallow import ValidationError
from main_app_utilities.command_and_control.schema import AttackSchema
from main_app_utilities.gcp.cloud_env import CloudEnv
from main_app_utilities.gcp.bucket_manager import BucketManager
from main_app_utilities.gcp.datastore_manager import DataStoreManager
from main_app_utilities.gcp.pubsub_manager import PubSubManager
from main_app_utilities.globals import BuildConstants, DatastoreKeyTypes, PubSub, get_current_timestamp_utc
import random
import string


class AttackSpecToCloud:
    """
    Prepares the build of workouts based on a YAML specification by storing the information in the
    cloud datastore.
    :@param attack_spec: The specification for building the Inject or Weakness
    :@param debug: Whether to publish to cloud functions or debug the build operations.
    """
    def __init__(self, cyber_arena_attack, debug=False):
        self.env = CloudEnv()
        # log_client = logging_v2.Client()
        # log_client.setup_logging()
        self.cyber_arena_attack = cyber_arena_attack
        self.datastore_manager = DataStoreManager()
        self.debug = debug
        self.parent_build_type = self.cyber_arena_attack.get('parent_build_type', BuildConstants.BuildType.FIXED_ARENA_CLASS.value)
        self.build_type = self.cyber_arena_attack.get('build_type', self.parent_build_type)
        if 'mode' not in self.cyber_arena_attack:
            raise ValidationError(f'Invalid mode given in {self.__class__.__name__}')
        self.cyber_arena_attack['creation_timestamp'] = get_current_timestamp_utc()
        self.pubsub_manager = PubSubManager(topic=PubSub.Topics.CYBER_ARENA.value)
        self.mode = self.cyber_arena_attack['mode']

        if self.mode == BuildConstants.BuildType.FIXED_ARENA_ATTACK.value:
            self.attack_id = ''.join(random.choice(string.ascii_lowercase) for j in range(10))
            self.cyber_arena_attack['id'] = self.attack_id
            self.args = self.cyber_arena_attack['args']
            self.cyber_arena_attack = AttackSchema().load(self.cyber_arena_attack)
            self.cyber_arena_attack['logs'] = []
            self.datastore_manager = DataStoreManager(key_type=DatastoreKeyTypes.CYBERARENA_ATTACK.value,
                                                      key_id=self.attack_id)
        else:
            raise ValidationError(f'Unrecognized value ({self.mode}) for BuildType in BuildAttackToCloud')

    def commit(self):
        """Sends PubSub request for requested inject build"""
        self.datastore_manager.put(self.cyber_arena_attack)
        if not self.debug:
            self.pubsub_manager.msg(handler=str(PubSub.Handlers.AGENCY.value), build_id=str(self.attack_id),
                                    action=str(self.mode), build_type=str(self.build_type),
                                    parent_id=str(self.cyber_arena_attack['parent_id']))
