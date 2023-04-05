import random
import flask
import yaml
from datetime import datetime, timedelta, timezone
from flask import json, request, session, redirect, url_for
from flask.views import MethodView
from api.utilities.decorators import instructor_required
from api.utilities.http_response import HttpResponse
from main_app_utilities.gcp.cloud_env import CloudEnv
from main_app_utilities.gcp.datastore_manager import DataStoreManager
from main_app_utilities.gcp.pubsub_manager import PubSubManager
from main_app_utilities.gcp.bucket_manager import BucketManager
from main_app_utilities.globals import PubSub, DatastoreKeyTypes, BuildConstants, Buckets, WorkoutStates
from main_app_utilities.infrastructure_as_code.build_spec_to_cloud import BuildSpecToCloud
from main_app_utilities.lms.lms_spec_decorator import LMSSpecDecorator

__author__ = "Andrew Bomberger"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Andrew Bomberger", "Philip Huff"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class Unit(MethodView):
    """Method View to handle API requests for Cyber Arena Units"""
    decorators = [instructor_required]

    def __init__(self):
        self.key_type = DatastoreKeyTypes.UNIT.value
        self.pubsub_actions = PubSub.Actions
        self.handler = PubSub.Handlers
        self.http_resp = HttpResponse
        self.env = CloudEnv()
        self.env_dict = self.env.get_env()
        self.pubsub_mgr = PubSubManager(topic=PubSub.Topics.CYBER_ARENA, env_dict=self.env_dict)
        self.bm = BucketManager(env_dict=self.env_dict)

    def get(self, build_id=None):
        if build_id:
            args = request.args
            if args.get("state", None):
                # Returns state for all workouts in unit
                states = []
                workouts = DataStoreManager().get_children(DatastoreKeyTypes.WORKOUT, build_id)
                if workouts:
                    exists = True
                    states = [{'id': workout['id'], 'state': WorkoutStates(workout['state']).name.lower()} for workout in workouts]
                else:
                    exists = False
                    states = []
                return self.http_resp(code=200, data={'exists': exists, 'states': states}).prepare_response()
            unit = DataStoreManager(key_type=self.key_type, key_id=build_id).get()
            if unit:
                return self.http_resp(code=200, data=unit).prepare_response()
            return self.http_resp(code=404).prepare_response()
        return self.http_resp(code=400).prepare_response()

    def post(self):
        user_email = session.get('user_email', None)
        recv_data = request.form

        # Parse Form Data
        expire_datetime = recv_data.get('expires', None)
        registration_required = recv_data.get('registration_required', False)
        build_type = recv_data.get('build_file', None)
        build_count = recv_data.get('build_count', None)

        # Send build request
        if build_count and expire_datetime and build_type:
            build_spec = DataStoreManager(key_type=DatastoreKeyTypes.CATALOG.value, key_id=build_type).get()
            if not build_spec:
                return self.http_resp(code=404, msg=f"Invalid build type {build_type}").prepare_response()
            build_spec['instructor_id'] = user_email
            expire_ts = int(datetime.strptime(expire_datetime.replace("T", " "), "%Y-%m-%d %H:%M").timestamp())
            build_spec['workspace_settings'] = {
                'count': build_count,
                'registration_required': registration_required,
                'student_emails': [],
                'expires': expire_ts
            }
            build_spec['join_code'] = ''.join(str(random.randint(0, 9)) for num in range(0, 6))
            if 'lms_quiz' in build_spec:
                build_spec = LMSSpecDecorator(build_spec=build_spec).decorate()

            build_spec_to_cloud = BuildSpecToCloud(cyber_arena_spec=build_spec, env_dict=self.env_dict)
            build_spec_to_cloud.commit(publish=False)
            return redirect(url_for('teacher_app.workout_list', unit_id=build_spec_to_cloud.get_build_id()))
        return self.http_resp(code=400).prepare_response()

    @instructor_required
    def delete(self, build_id=None):
        if build_id:
            self.pubsub_mgr.msg(handler=str(self.handler.CONTROL.value), build_id=str(build_id),
                                action=str(self.pubsub_actions.DELETE.value),
                                cyber_arena_object=str(PubSub.CyberArenaObjects.UNIT.value))
            return self.http_resp(code=200).prepare_response()
        return self.http_resp(code=400).prepare_response()

    @instructor_required
    def put(self, build_id):
        if build_id:
            args = request.json
            action = args.get('action', None)
            question_id = args.get('question_id', None)
            child_id = args.get('build_id', None)

            valid_actions = [PubSub.Actions.START.value, PubSub.Actions.STOP.value, PubSub.Actions.NUKE]
            if action and action in valid_actions:
                self.pubsub_mgr.msg(handler=str(PubSub.Handlers.CONTROL.value), action=str(action),
                                    build_id=str(build_id),
                                    cyber_arena_object=str(PubSub.CyberArenaObjects.UNIT.value))
                return self.http_resp(code=200).prepare_response()
            elif question_id and child_id:
                """For cases where an assessment question needs manual grading"""
                workout = DataStoreManager(key_type=DatastoreKeyTypes.WORKOUT, key_id=child_id).get()
                if workout:
                    for question in workout['assessment']:
                        if question['id'] == question:
                            question['complete'] = True
                            break
                    DataStoreManager(key_type=DatastoreKeyTypes.WORKOUT, key_id=build_id).put(workout)
                return self.http_resp(code=404, msg="NO BUILD FOUND").prepare_response()
        return self.http_resp(code=400, msg="BAD REQUEST").prepare_response()
