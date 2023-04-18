"""
Decorates the build spec with the required dynamic elements of the schema based on user inputs.
"""
from datetime import datetime, timedelta
from canvasapi import Canvas

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


class LMSSpecDecorator:
    def __init__(self, build_spec, course_code, due_at=None, time_limit=None, allowed_attempts=None):
        self.build_spec = build_spec
        self.course_code = course_code
        self.instructor_id = self.build_spec.get('instructor_id', None)
        self.due_at = due_at if due_at else (datetime.utcnow() + timedelta(days=30)).strftime('%Y-%m-%dT%H:%M:%SZ')
        self.time_limit = time_limit
        self.allowed_attempts = allowed_attempts if allowed_attempts else -1
        self.ds = DataStoreManager()
        self.settings = None
        self.lms_type = None

    def decorate(self):
        instructor = self.ds.get(key_type=DatastoreKeyTypes.USER, key_id=self.instructor_id)
        if not instructor or 'settings' not in instructor:
            raise LMSSpecNoInstructorSettingsError
        self.settings = instructor['settings']

        self.lms_type = self.build_spec['lms_quiz']['lms_type']
        if self.lms_type == BuildConstants.LMS.CANVAS:
            lms_connection = self._get_canvas_connection()
        else:
            raise LMSSpecLMSTypeNotSupported(f"LMS {self.lms_type} is not supported")

        self.build_spec['lms_quiz']['lms_connection'] = lms_connection
        self.build_spec['lms_quiz'].update({
            'description': '',
            'due_at': self.due_at,
            'time_limit': self.time_limit,
            'allowed_attempts': self.allowed_attempts
        })
        return self.build_spec

    def _get_canvas_connection(self):
        try:
            api_key = self.settings['canvas_api_key']
            url = self.settings['url']
        except ValueError:
            raise LMSSpecIncompleteInstructorSettingsError(f"Missing instructor settings for the LMS {self.lms_type}")

        canvas = Canvas(url, api_key)
        canvas.get_course(self.course_code)
        connection = {
            'api_key': api_key,
            'url': url,
            'course_code': self.course_code
        }
        return connection


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
