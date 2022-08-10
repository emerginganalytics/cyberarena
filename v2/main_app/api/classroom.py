import json
from flask import request
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
        user_data = request.json
        user_email = user_data.get('user_email', None)
        if user_email:
            if class_name:
                class_query = DataStoreManager(key_id=str(user_email)).get_classroom(class_name=class_name)
            else:
                class_query = DataStoreManager(key_id=str(user_email)).get_classroom()
            class_list = []
            for class_object in class_query:
                class_list.append(class_object)
            return json.dumps(class_list)
        return self.http_resp(code=400)

    def post(self):
        """Create Classroom"""
        return self.http_resp(code=400)

    def delete(self, class_name=None):
        return self.http_resp(code=405)

    def put(self, class_name=None):
        """Update Existing Classroom"""
        recv_data = request.json
        return self.http_resp(code=400)
