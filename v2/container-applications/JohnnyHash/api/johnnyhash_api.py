import yaml
from datetime import datetime, timedelta, timezone
from flask import request, session, url_for, redirect
from flask.views import MethodView

from api.utilities.http_response import HttpResponse
from app_utilities.crypto_suite.hashes import Hashes, HashErrors
from app_utilities.gcp.cloud_env import CloudEnv
from app_utilities.gcp.datastore_manager import DataStoreManager
from app_utilities.globals import DatastoreKeyTypes, BuildConstants

__author__ = "Andrew Bomberger"
__copyright__ = "Copyright 2023, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Andrew Bomberger"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class JohnnyHashAPI(MethodView):
    def __init__(self, debug=False):
        self.env = CloudEnv()
        self.ds = DataStoreManager()
        self.http_resp = HttpResponse
        self.debug = debug

    def get(self, build_id=None):
        if build_id:
            return self.http_resp(code=200).prepare_response()
        return self.http_resp(code=400).prepare_response()

    def post(self, build_id=None):
        if build_id:
            if 'password_file' not in request.files:
                return self.http_resp(code=404, msg=HashErrors.NO_FILE_SUBMITTED).prepare_response()
            else:
                input_file = request.files['password_file']
                hashes = Hashes().validate_hashes_from_file(input_file)
                if type(hashes) != list:
                    return self.http_resp(code=400, msg=HashErrors.EMPTY_FILE).prepare_response()
                return self.http_resp(code=200, data=hashes).prepare_response()
        return self.http_resp(code=400).prepare_response()

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
