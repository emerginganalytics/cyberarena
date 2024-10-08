"""
Parses yaml according to version 2 of the Cyber Arena specification and stores a build structure in the cloud datastore.

We use marshmallow to perform serializer validation only. We define the required schemas in WorkoutComputeSchema,
WorkoutContainerSchema, ArenaSchema, and perhaps more. New fields in the yaml should be accounted for in the schema
validation.
"""
from datetime import datetime, timezone
from marshmallow import ValidationError
from google.cloud import logging_v2
import random
import string

from main_app_utilities.globals import BuildConstants, DatastoreKeyTypes, PubSub, get_current_timestamp_utc
from main_app_utilities.infrastructure_as_code.schema import FixedArenaSchema, FixedArenaClassSchema, UnitSchema
from main_app_utilities.gcp.cloud_env import CloudEnv
from main_app_utilities.gcp.datastore_manager import DataStoreManager
from main_app_utilities.gcp.pubsub_manager import PubSubManager
from main_app_utilities.global_objects.agent import Agent
from main_app_utilities.infrastructure_as_code.object_validators.unit_object_validator import UnitValidator

__author__ = "Philip Huff"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class BuildSpecToCloud:
    def __init__(self, cyber_arena_spec, env_dict=None, debug=False):
        """
        Prepares the build of workouts based on a YAML specification by storing the information in the
        cloud datastore.
        :@param cyber_arena_spec: The specification for building the Cyber Arena
        :@param debug: Whether to publish to cloud functions or debug the build operations.
        """
        self.env = CloudEnv(env_dict=env_dict) if env_dict else CloudEnv()
        self.debug = debug
        log_client = logging_v2.Client()
        log_client.setup_logging()
        if 'build_type' not in cyber_arena_spec:
            raise ValidationError

        if self.debug:
            cyber_arena_spec['test'] = True
        cyber_arena_spec['creation_timestamp'] = get_current_timestamp_utc()
        self.pubsub_manager = PubSubManager(topic=PubSub.Topics.CYBER_ARENA.value, env_dict=self.env.get_env())
        self.build_type = cyber_arena_spec['build_type']
        if self.build_type == BuildConstants.BuildType.FIXED_ARENA.value:
            self.build_id = cyber_arena_spec['id']
            self.cyber_arena_spec = FixedArenaSchema().load(cyber_arena_spec)
            self.datastore_manager = DataStoreManager(key_type=DatastoreKeyTypes.FIXED_ARENA.value,
                                                      key_id=self.build_id)
            self.action = PubSub.BuildActions.FIXED_ARENA.value
        elif self.build_type == BuildConstants.BuildType.FIXED_ARENA_CLASS.value:
            self.build_id = ''.join(random.choice(string.ascii_lowercase) for j in range(10))
            cyber_arena_spec['id'] = self.build_id
            self.cyber_arena_spec = FixedArenaClassSchema().load(cyber_arena_spec)
            self.datastore_manager = DataStoreManager(key_type=DatastoreKeyTypes.FIXED_ARENA_CLASS.value,
                                                      key_id=self.build_id)
            self.action = PubSub.BuildActions.FIXED_ARENA_CLASS.value
        elif self.build_type in [BuildConstants.BuildType.UNIT.value, BuildConstants.BuildType.ESCAPE_ROOM.value]:
            self.build_id = ''.join(random.choice(string.ascii_lowercase) for j in range(10))
            cyber_arena_spec['id'] = self.build_id
            cyber_arena_spec = UnitSchema().load(cyber_arena_spec)
            self.cyber_arena_spec = UnitValidator().load(cyber_arena_spec)
            self.datastore_manager = DataStoreManager(key_type=DatastoreKeyTypes.UNIT.value, key_id=self.build_id)
            self.action = PubSub.BuildActions.UNIT.value

    def commit(self, publish=True):
        self.datastore_manager.put(self.cyber_arena_spec)
        if not self.debug:
            if publish:
                self.pubsub_manager.msg(handler=str(PubSub.Handlers.BUILD.value), action=str(self.action),
                                        build_id=str(self.build_id))

    def get_build_id(self):
        return self.build_id
