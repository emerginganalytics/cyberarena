from flask import request, session, url_for, redirect
from flask.views import MethodView

from api.utilities.http_response import HttpResponse
from api.utilities.assessment import AssessmentManager
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


class ClassifiedAPI(MethodView):
    def __init__(self, debug=False):
        self.env = CloudEnv()
        self.ds = DataStoreManager()
        self.http_resp = HttpResponse
        self.debug = debug

    def get(self, build_id=None):
        pass

    def post(self):
        if form := request.form:
            build_id = form.get('build_id', None)
            question_id = form.get('build_id', None)
            submission = form.get('submission', None)
            if build_id and question_id and submission:
                correct = AssessmentManager(build_id=build_id).evaluate(question_id=question_id, submission=submission)


    def put(self, build_id=None):
        if build_id:
            if build := self.ds.get(key_type=DatastoreKeyTypes.WORKOUT, key_id=build_id):

                return self.http_resp(code=200).prepare_response()
        return self.http_resp(code=400).prepare_response()

# [ eof ]
