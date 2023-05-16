"""
A base parent class for the LMS object in the Cyber Arena
"""

from abc import ABC, abstractmethod

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
