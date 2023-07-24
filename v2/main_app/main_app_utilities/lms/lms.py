"""
A base parent class for the LMS object in the Cyber Arena
"""
from datetime import datetime, timedelta
from canvasapi import Canvas
from abc import ABC, abstractmethod

from main_app_utilities.globals import DatastoreKeyTypes, BuildConstants
from main_app_utilities.gcp.datastore_manager import DataStoreManager

__author__ = "Philip Huff"
__copyright__ = "Copyright 2023, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff"]
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class LMS:
    def __init__(self, url, api_key, course_code):
        self.url = url
        self.api_key = api_key
        self.course_code = course_code
        self.students = []
        self.quiz = []
        self.question = []

    def get_class_list(self):
        raise NotImplementedError("get_class_list not implemented for this object.")

    def mark_question_complete(self, quiz_id, student_email, question_id):
        raise NotImplementedError("mark_question_complete not implemented for this object.")

    def validate_connection(self):
        raise NotImplementedError("validate_connection not implemented for this object.")


class LMSSpec:
    def __init__(self, build_spec, course_code, lms_type, due_at=None, time_limit=None, allowed_attempts=None):
        self.build_spec = build_spec
        self.course_code = course_code
        self.instructor_id = self.build_spec.get('instructor_id', None)
        self.due_at = due_at if due_at else (datetime.utcnow() + timedelta(days=30)).strftime('%Y-%m-%dT%H:%M:%SZ')
        self.time_limit = time_limit
        self.allowed_attempts = allowed_attempts if allowed_attempts else -1
        self.ds = DataStoreManager()
        self.settings = None
        self.lms_type = lms_type

    def decorate(self):
        instructor = self.ds.get(key_type=DatastoreKeyTypes.USERS, key_id=self.instructor_id)
        if not instructor or 'settings' not in instructor:
            raise LMSSpecNoInstructorSettingsError
        self.settings = instructor['settings']
        self.build_spec['lms_connection'] = self._get_connection()
        if 'questions' in self.build_spec:
            self.build_spec['lms_quiz']['questions'] = self._decorate_questions(
                self.build_spec['lms_quiz']['questions'])
        if 'lms_quiz' in self.build_spec:
            self.build_spec['lms_quiz'].update({
                'description': '',
                'due_at': str(self.due_at),
                'allowed_attempts': self.allowed_attempts
            })
        return self.build_spec

    def _get_connection(self):
        pass

    def _decorate_questions(self, questions):
        pass


class LMSSpecError(Exception):
    pass

class LMSSpecNoInstructorSettingsError(LMSSpecError):
    pass

class LMSSpecIncompleteInstructorSettingsError(LMSSpecError):
    pass

class LMSSpecConnectionError(LMSSpecError):
    pass

class LMSSpecLMSTypeNotSupported(LMSSpecError):
    pass


class LMSExceptionWithHttpStatus(Exception):
    def __init__(self, message, http_status_code=400):
        super().__init__(message)
        self.http_status_code = http_status_code
class LMSUserNotFound(Exception):
    pass
