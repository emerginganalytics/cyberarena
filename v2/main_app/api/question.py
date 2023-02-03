"""
API Endpoint to handle question submissions for assessment questions with type 'auto'
"""
__author__ = "Philip Huff"
__copyright__ = "Copyright 2023, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"

import yaml
from datetime import datetime, timedelta, timezone
from flask import request, session, url_for, redirect
from flask.views import MethodView

from api.utilities.http_response import HttpResponse
from main_app_utilities.infrastructure_as_code.schema import EscapeRoomSchema, PuzzleSchema
from main_app_utilities.gcp.datastore_manager import DataStoreManager
from main_app_utilities.gcp.pubsub_manager import PubSubManager
from main_app_utilities.gcp.cloud_env import CloudEnv
from main_app_utilities.gcp.bucket_manager import BucketManager
from main_app_utilities.globals import PubSub, DatastoreKeyTypes, BuildConstants, Buckets
from main_app_utilities.infrastructure_as_code.build_spec_to_cloud import BuildSpecToCloud


class Answer:
    def __init__(self):
        pass

    def post(self, build_id=None):
        question_id = ''
