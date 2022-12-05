from marshmallow import ValidationError
from main_app_utilities.command_and_control.attack_schema import AttackSchema
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
        # Uncomment the following two lines
        # log_client = logging_v2.Client()
        # log_client.setup_logging()
        self.datastore_manager = DataStoreManager()
        self.debug = debug
        if 'build_type' not in cyber_arena_attack:
            raise ValidationError

        cyber_arena_attack['creation_timestamp'] = get_current_timestamp_utc()
        self.pubsub_manager = PubSubManager(topic=PubSub.Topics.CYBER_ARENA.value)
        self.build_type = cyber_arena_attack['build_type']
        if self.build_type == BuildConstants.BuildType.FIXED_ARENA_ATTACK.value:
            self.build_id = ''.join(random.choice(string.ascii_lowercase) for j in range(10))
            cyber_arena_attack['id'] = self.build_id
            self.args = cyber_arena_attack['args']
            self.cyber_arena_attack = AttackSchema().load(cyber_arena_attack)
            self.cyber_arena_attack['logs'] = []
            self.datastore_manager = DataStoreManager(key_type=DatastoreKeyTypes.CYBERARENA_ATTACK.value,
                                                      key_id=self.build_id)

    def update(self):
        """
        Updates Datastore with existing attack email_templates
        :return:
        """
        attack_specs = BucketManager().get_attacks()
        # Make sure that the spec file exists in project
        if not attack_specs:
            raise ValidationError
        for attack in attack_specs['attack']:
            if 'id' not in attack:
                raise ValidationError
            attack_id = attack['id']
            self.datastore_manager.set(key_type=DatastoreKeyTypes.CYBERARENA_ATTACK_SPEC.value, key_id=attack_id)
            attack_spec_obj = AttackSchema().load(attack)

            # Obj is validated; Update datastore entity
            self.datastore_manager.put(attack_spec_obj)

    def commit(self):
        """Sends PubSub request for requested inject build"""
        self.datastore_manager.put(self.cyber_arena_attack)
        if not self.debug:
            self.pubsub_manager.msg(handler=str(PubSub.Handlers.BOTNET.value), action=str(self.action),
                                    build_id=str(self.build_id), expires=str(self.expires), args=str(self.args))