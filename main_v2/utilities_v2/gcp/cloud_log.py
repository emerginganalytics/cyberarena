from google.cloud import logging_v2
from enum import Enum

__author__ = "Andrew Bomberger"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Andrew Bomberger", "Philip Huff"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class CloudLog:
    """
    Class to log messages to Google Cloud project.
    @param logging_id: The facility to log under
    @param severity: LOG_LEVELS
    @type severity: Integer
    @return: None
    """
    def __init__(self, logging_id, severity):
        self.log_client = logging_v2.Client()
        self.logging_id = logging_id
        self.severity = severity

    class LogLevels(Enum):
        """GCP Logging API Severity Levels"""
        DEBUG = 100
        INFO = 200
        NOTICE = 300
        WARNING = 400
        ERROR = 500
        CRITICAL = 600
        ALERT = 700
        EMERGENCY = 800

    class LogIDS(str, Enum):
        MAIN_APP = 'cyberarena-app'
        USER_AUTHORIZATION = 'cyberarena-login'
        STUDENT_APP = 'student-app'
        TEACHER_APP = 'teacher-app'
        ADMIN_APP = 'admin-app'
        APP_ERRORS = 'cybergym-app-errors'
        API = 'cyberarena-api'

    def create_log(self, message, **kwargs):
        """
        Creates log event based on passed arguments
        @param message: Logging message
        """
        g_logger = self.log_client.logger(self.logging_id)
        g_logger.log_struct(
            {
                "message": message,
                "details": str([kwargs])
            }, severity=self.severity
        )
