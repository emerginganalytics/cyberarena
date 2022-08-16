from marshmallow import ValidationError
from main_app_utilities.globals import BuildConstants, DatastoreKeyTypes, PubSub, get_current_timestamp_utc
from main_app_utilities.gcp.bucket_manager import BucketManager
from main_app_utilities.gcp.cloud_env import CloudEnv
from main_app_utilities.gcp.datastore_manager import DataStoreManager
from main_app_utilities.command_and_control.schema import AttackSchema


class AttackSpecToCloud:
    """
    Takes input attack spec object and creates an attack datastore object to use
    for builds

    TODO: Currently this was built for uploading the attack specs to cyberarena-attack-spec;
          Need to rework to create cyberarena-attack or command_and_control object instead.
    """
    def __init__(self, debug=False):
        self.env = CloudEnv()
        self.debug = debug
        self.attack_specs = BucketManager().get_attacks()
        self.datastore_manager = DataStoreManager()

        # Make sure that the spec file exists in project
        if not self.attack_specs:
            raise ValidationError

    def update(self):
        for attack in self.attack_specs['attack']:
            if 'id' not in attack:
                raise ValidationError
            attack_id = attack['id']
            self.datastore_manager.set(key_type=DatastoreKeyTypes.CYBERARENA_ATTACK_SPEC.value,
                                       key_id=attack_id)
            attack_spec_obj = AttackSchema().load(attack)

            # Obj is validated; Update datastore entity
            self.datastore_manager.put(attack_spec_obj)

    def commit(self):
        pass
