import json
from flask import abort, request, session, jsonify
from flask.views import MethodView
from api.decorators import auth_required, admin_required, instructor_required
from utilities.gcp.datastore_manager import DataStoreManager
from utilities.globals import DatastoreKeyTypes


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
        abort(400)

    def post(self, class_name=None):
        """Create Classroom"""
        pass

    def delete(self, class_name=None):
        abort(405)

    def put(self, class_name=None):
        """Update Existing Classroom"""
        recv_data = request.json
        pass
