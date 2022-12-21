import json
from flask import request, session
from flask.views import MethodView
from api.utilities.decorators import instructor_required
from api.utilities.http_response import HttpResponse
from main_app_utilities.gcp.datastore_manager import DataStoreManager

__author__ = "Andrew Bomberger"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Andrew Bomberger"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class Classroom(MethodView):
    decorators = [instructor_required]

    def __init__(self):
        self.http_resp = HttpResponse

    def get(self, class_name=None):
        """Get Classroom"""
        user_email = session.get('user_email', None)
        if user_email:
            if class_name:
                class_query = DataStoreManager(key_id=str(user_email)).get_classroom(class_name=class_name)
            else:
                class_query = DataStoreManager(key_id=str(user_email)).get_classroom()
            if class_query:
                return self.http_resp(code=200, data=class_query).prepare_response()
            return self.http_resp(code=404, data=[]).prepare_response()
        return self.http_resp(code=400).prepare_response()

    def post(self):
        """Create Classroom"""
        return self.http_resp(code=400).prepare_response()

    def delete(self, class_name=None):
        return self.http_resp(code=405).prepare_response()

    def put(self, class_name=None):
        """Update Existing Classroom"""
        recv_data = request.json
        return self.http_resp(code=400).prepare_response()
