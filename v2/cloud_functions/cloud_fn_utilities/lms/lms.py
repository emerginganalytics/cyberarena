"""
A base parent class for the LMS object in the Cyber Arena
"""

import random
import string
from abc import ABC, abstractmethod

from cloud_fn_utilities.globals import DatastoreKeyTypes
from cloud_fn_utilities.gcp.cloud_logger import Logger
from cloud_fn_utilities.gcp.datastore_manager import DataStoreManager


__author__ = "Philip Huff"
__copyright__ = "Copyright 2023, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff"]
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class LMS:
    def __init__(self, url, api_key, course_code, build):
        self.logger = Logger("cloud_functions.cloud_env").logger
        self.url = url
        self.api_key = api_key
        self.course_code = course_code
        self.build = build
        self.students = []

    def get_class_list(self):
        raise NotImplementedError("get_class_list not implemented for this object.")

    def create_quiz(self):
        raise NotImplementedError("create_quiz not implemented for this object.")

    def create_assignment(self):
        raise NotImplementedError("create_quiz not implemented for this object.")
