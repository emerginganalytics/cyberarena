import json
import random
import string
from flask import request, session
from flask.views import MethodView
from api.utilities.decorators import instructor_required
from api.utilities.http_response import HttpResponse
from main_app_utilities.gcp.datastore_manager import DataStoreManager
from main_app_utilities.globals import DatastoreKeyTypes

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
        self.ds_manager = DataStoreManager()
        self.key_type = DatastoreKeyTypes.CLASSROOM.value

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
        form_data = request.json
        # Get class attr
        instructor_id = form_data.get('instructor_email', None)
        class_name = form_data.get('class_name', None)
        student_auth = form_data.get('student_auth', None)
        if class_name and student_auth and instructor_id:
            roster = []
            if 'student_count' in form_data and form_data['student_count'] != '':
                roster = [f'Student {i + 1}' for i in range(int(form_data['student_count']))]
            class_id = ''.join(random.choice(string.ascii_lowercase) for j in range(10))
            new_class = {
                'class_id': class_id,
                'class_name': class_name,
                'student_auth': student_auth,
                'teacher_email': instructor_id,
                'unit_list': [],
                'roster': roster,
            }
            self.ds_manager.set(key_type=self.key_type, key_id=class_id)
            self.ds_manager.put(new_class)
            return self.http_resp(code=200).prepare_response()
        return self.http_resp(code=400).prepare_response()

    def delete(self, class_name=None):
        instructor_id = session.get('user_email', None)
        is_admin = True if 'admins' in session.get('user_groups') else False
        if class_name and instructor_id:
            self.ds_manager.set(key_type=self.key_type, key_id=str(class_name))
            class_obj = self.ds_manager.get()
            if class_obj:
                if instructor_id == class_obj['teacher_email'] or is_admin:
                    self.ds_manager.delete()
                    return self.http_resp(code=200).prepare_response()
                else:
                    return self.http_resp(code=403).prepare_response()
        return self.http_resp(code=400).prepare_response()

    def put(self, class_name=None):
        """Update Existing Classroom"""
        recv_data = request.json
        return self.http_resp(code=400).prepare_response()
