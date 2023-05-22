"""

"""
import random
import string
from canvasapi import Canvas
from canvasapi.submission import Submission

from main_app_utilities.lms.lms import LMS, LMSSpec, LMSSpecIncompleteInstructorSettingsError

__author__ = "Philip Huff"
__copyright__ = "Copyright 2023, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff"]
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class LMSCanvas(LMS):
    def __init__(self, url, api_key, course_code=None):
        super().__init__(url, api_key, course_code)
        self.canvas = Canvas(self.url, self.api_key)
        self.course = self.canvas.get_course(self.course_code) if course_code else None

    def get_class_list(self):
        self.students = self.course.get_users(enrollment_type=['student'])
        return self.students

    def get_courses(self):
        courses = self.canvas.get_courses()
        return {x.id: x.name for x in courses}

    def mark_question_correct(self, quiz_id, student_email, added_points):
        submission = self._get_submission(student_email, quiz_id)
        score = submission.score + added_points if submission.score else added_points
        submission.edit(submission={'posted_grade': score})

    def _get_submission(self, student_email, quiz_id):
        selected_assignment = None
        assignments = list(self.course.get_assignments())
        for assignment in assignments:
            if assignment.quiz_id == quiz_id:
                selected_assignment = assignment
                break
        if not selected_assignment:
            raise
        users = list(self.course.get_users(search_term=student_email))
        user_id = users[0].id if len(users) > 0 else None
        submission = selected_assignment.get_submission(user_id)
        return submission


class LMSSpecCanvas(LMSSpec):
    def __init__(self, build_spec, course_code, lms_type, due_at=None, time_limit=None, allowed_attempts=None):
        super().__init__(build_spec, course_code, lms_type, due_at, time_limit, allowed_attempts)

    def _get_connection(self):
        try:
            api_key = self.settings[self.lms_type]['api']
            url = self.settings[self.lms_type]['url']
        except ValueError:
            raise LMSSpecIncompleteInstructorSettingsError(f"Missing instructor settings for the LMS {self.lms_type}")

        canvas = Canvas(url, api_key)
        canvas.get_course(self.course_code)
        connection = {
            'lms_type': self.lms_type,
            'api_key': api_key,
            'url': url,
            'course_code': self.course_code
        }
        return connection

    def _decorate_questions(self, questions):
        """
        Modify the questions and replace script_assessment questions with those that can be inserted by the quiz.
        Args:
            questions (list): A list of questions

        Returns:

        """
        for question in questions:
            if 'name' in question:
                question['question_name'] = question.pop('name')
            if 'script_assessment' in question and question['script_assessment']:
                random_answer = ''.join(random.choice(string.ascii_letters) for i in range(12))
                question.update({
                    'question_type': 'short_answer_question',
                    'answers': [{'answer_text': random_answer, 'weight': '100'}]
                })
        return questions
