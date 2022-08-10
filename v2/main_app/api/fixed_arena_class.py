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
            fa_class = DataStoreManager(key_id=self.kind).query(filter_key='id', op='=', value=build_id)
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
            # Check for any currently running classes for specific fixed-arena
            class_query = DataStoreManager(key_id=self.kind).query()
            class_query.add_filter('parent_id', '=', stoc_id)
            # TODO: Verify that this is the correct check state
            class_query.add_filter('state', '=', str(BuildConstants.FixedArenaClassStates.RUNNING.value))
            class_list = list(class_query.fetch())

            # If class doesn't exist, init build request
            if not class_list:
                fixed_arena_yaml = self.bm.get(bucket=self.env.spec_bucket,
                                               file=f"{Buckets.Folders.SPECS}{build_id}.yaml")
                build_spec = yaml.safe_load(fixed_arena_yaml)
                expire_ts = int(datetime.strptime(expire_datetime.replace("T", " "), "%Y-%m-%d %H:%M").timestamp())
                print(expire_ts)
                build_spec['workspace_settings'] = {
                    'count': build_count,
                    'registration_required': registration_required,
                    'student_list': [],
                    'expires': expire_ts
                }
                build_spec_to_cloud = BuildSpecToCloud(cyber_arena_spec=build_spec, debug=False)
                build_spec_to_cloud.commit()
                return self.http_resp(code=200).prepare_response()
            return self.http_resp(code=409).prepare_response()
        return self.http_resp(code=400).prepare_response()

    @instructor_required
    def delete(self, build_id=None):
        if build_id:
            print(f'delete request for {build_id}')
            """ TODO: uncomment for production use
            self.pubsub_mgr.msg(handler=self.handler.CONTROL, build_id=build_id,
                                action=self.pubsub_actions.DELETE,
                                cyber_arena_object=PubSub.CyberArenaObjects.FIXED_ARENA_CLASS)"""
            return self.http_resp(code=200).prepare_response()
        return self.http_resp(code=400).prepare_response()

    @instructor_required
    def put(self, build_id=None):
        if build_id:
            args = request.json
            action = args.get('action', None)
            valid_actions = [PubSub.Actions.START.value, PubSub.Actions.STOP.value]
            if action and action in valid_actions:
                self.pubsub_mgr.msg(handler=PubSub.Handlers.CONTROL, action=action, build_id=build_id)
                return self.http_resp(code=200).prepare_response()
        return self.http_resp(code=400).prepare_response()

