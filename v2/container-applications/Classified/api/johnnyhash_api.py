from flask import request, session, url_for, redirect
from flask.views import MethodView

from api.utilities.http_response import HttpResponse
from api.utilities.assessment import AssessmentManager
from app_utilities.crypto_suite.hashes import Hashes
from app_utilities.crypto_suite.ciphers import Ciphers
from app_utilities.gcp.cloud_env import CloudEnv
from app_utilities.gcp.datastore_manager import DataStoreManager
from app_utilities.globals import DatastoreKeyTypes, BuildConstants, Algorithms, CipherModes

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

    def post(self):
        if json_data := request.json:
            passwords = json_data.get('passwords')
            hashes = Hashes().generate_hashes(passwords)
            return self.http_resp(code=200, data=hashes).prepare_response()
        return self.http_resp(code=400).prepare_response()


class JohnnyCipherAPI(MethodView):
    def __init__(self, debug=False):
        self.env = CloudEnv()
        self.ds = DataStoreManager()
        self.http_resp = HttpResponse
        self.debug = debug
        self.build = dict()

    def post(self):
        if form := request.form:
            message = form.get('message', None)
            key = form.get('key', None)
            if message and key:
                cipher = Ciphers(algorithm=Algorithms.CAESAR, mode=CipherModes.DECRYPT, message=message, key=key).get()
                return self.http_resp(code=200, data=cipher).prepare_response()
            return self.http_resp(code=400, msg='Missing cipher message/key').prepare_response()
        return self.http_resp(code=400).prepare_response()

    def put(self, build_id=None):
        if build_id:
            if build := self.ds.get(key_type=DatastoreKeyTypes.WORKOUT, key_id=build_id):
                if json_data := request.json:
                    submission = json_data.get('submission', None)
                    question_id = json_data.get('question_id', None)
                    if question_id and submission:
                        assessment = AssessmentManager(build_id=build_id, build=build)
                        complete, evaluated = assessment.evaluate(question_id=question_id, submission=submission)
                        return self.http_resp(code=200, data={'complete': complete,
                                                              'message': submission}).prepare_response()
                return self.http_resp(code=400).prepare_response()
            return self.http_resp(code=404).prepare_response()
        return self.http_resp(code=400).prepare_response()
