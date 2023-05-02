"""

"""

from canvasapi import Canvas

from main_app_utilities.lms.lms import LMS

__author__ = "Philip Huff"
__copyright__ = "Copyright 2023, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff"]
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class LMSCanvas(LMS):
    def __init__(self, url, api_key, course_code):
        super().__init__(url, api_key, course_code)
        self.canvas = Canvas(self.url, self.api_key)
        self.course = self.canvas.get_course(self.course_code)

    def get_class_list(self):
        self.students = self.course.get_users(enrollment_type=['student'])
        return self.students