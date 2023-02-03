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
from api.utilities.hashes import Hashes
from app_utilities.gcp.cloud_env import CloudEnv
from app_utilities.gcp.datastore_manager import DataStoreManager
from app_utilities.globals import DatastoreKeyTypes, BuildConstants


class JohnnyHash(MethodView):
    def __init__(self, debug=False):
        self.http_resp = HttpResponse
        self.env = CloudEnv()
        self.debug = debug
        self.ds = DataStoreManager()

    def get(self, build_id=None):
        return self.http_resp(code=200).prepare_response()

    def put(self, build_id=None):
        if build_id:
            recv_data = request.json
            if recv_data:
                question_id = recv_data.get('question_id', None)
                try:
                    Hashes(build_id=build_id).set_md5_hash(question_id)
                    return self.http_resp(200).prepare_response()
                except ValueError:
                    return self.http_resp(404).prepare_response()
        return self.http_resp(400).prepare_response()
