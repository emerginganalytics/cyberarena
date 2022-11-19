import yaml
from datetime import datetime, timedelta, timezone
from flask import json, request
from flask.views import MethodView
from api.utilities.decorators import instructor_required
from api.utilities.http_response import HttpResponse
from main_app_utilities.gcp.cloud_env import CloudEnv
from main_app_utilities.gcp.datastore_manager import DataStoreManager
from main_app_utilities.gcp.pubsub_manager import PubSubManager
from main_app_utilities.gcp.bucket_manager import BucketManager
from main_app_utilities.globals import PubSub, DatastoreKeyTypes, BuildConstants, Buckets
from main_app_utilities.infrastructure_as_code.build_spec_to_cloud import BuildSpecToCloud, BuildConstants

__author__ = "Andrew Bomberger"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Andrew Bomberger"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class FixedArenaClass(MethodView):
    def __init__(self):
        self.kind = DatastoreKeyTypes.FIXED_ARENA_CLASS.value
        self.pubsub_actions = PubSub.Actions
        self.handler = PubSub.Handlers
        self.http_resp = HttpResponse
        self.pubsub_mgr = PubSubManager(topic=PubSub.Topics.CYBER_ARENA)
        self.bm = BucketManager()
        self.env = CloudEnv()

    def get(self, build_id=None):
        if build_id:
            fa_class = DataStoreManager(key_type=DatastoreKeyTypes.FIXED_ARENA_CLASS.value, key_id=build_id).get()
            if fa_class:
                return self.http_resp(code=200, data=fa_class).prepare_response()
            return self.http_resp(code=404).prepare_response()
        return self.http_resp(code=400).prepare_response()

    @instructor_required
    def post(self):
        recv_data = request.json

        # Parse Form Data
        stoc_id = recv_data.get('stoc_id', None)
        build_count = recv_data.get('build_count', None)
        expire_datetime = recv_data.get('expires', None)
        registration_required = recv_data.get('registration_required', False)
        build_id = recv_data.get('build_id', None)

        # make sure that no running class already exists for fixed-arena
        if stoc_id and build_count and expire_datetime and build_id:
            parent_stoc = DataStoreManager(key_type=DatastoreKeyTypes.FIXED_ARENA.value, key_id=stoc_id).get()
            if parent_stoc:
                check_class = parent_stoc.get('active_class', None)
                if not check_class:
                    # No active class found; Initiate class build
                    fixed_arena_yaml = self.bm.get(bucket=self.env.spec_bucket,
                                                   file=f"{Buckets.Folders.SPECS}{build_id}.yaml")
                    build_spec = yaml.safe_load(fixed_arena_yaml)
                    expire_ts = int(datetime.strptime(expire_datetime.replace("T", " "), "%Y-%m-%d %H:%M").timestamp())
                    build_spec['workspace_settings'] = {
                        'count': build_count,
                        'registration_required': registration_required,
                        'student_emails': [],
                        'expires': expire_ts
                    }
                    build_spec['add_attacker'] = recv_data.get('add_attacker', False)
                    build_spec_to_cloud = BuildSpecToCloud(cyber_arena_spec=build_spec)
                    build_spec_to_cloud.commit()
                    return self.http_resp(code=200).prepare_response()
                # Requested STOC already has an active class; Return 409 CONFLICT
                return self.http_resp(code=409, msg="CONFLICT: Class already exists for requested STOC!").prepare_response()
        return self.http_resp(code=400).prepare_response()

    @instructor_required
    def delete(self, build_id=None):
        if build_id:
            self.pubsub_mgr.msg(handler=str(self.handler.CONTROL.value), build_id=str(build_id),
                                action=str(self.pubsub_actions.DELETE.value),
                                cyber_arena_object=str(PubSub.CyberArenaObjects.FIXED_ARENA_CLASS.value))
            return self.http_resp(code=200).prepare_response()
        return self.http_resp(code=400).prepare_response()

    @instructor_required
    def put(self, build_id=None):
        if build_id:
            args = request.json
            action = args.get('action', None)
            valid_actions = [PubSub.Actions.START.value, PubSub.Actions.STOP.value]
            if action and action in valid_actions:
                self.pubsub_mgr.msg(handler=str(PubSub.Handlers.CONTROL.value), action=str(action),
                                    build_id=str(build_id),
                                    cyber_arena_object=str(PubSub.CyberArenaObjects.FIXED_ARENA_CLASS.value))
                return self.http_resp(code=200).prepare_response()
        return self.http_resp(code=400, msg="BAD REQUEST").prepare_response()
