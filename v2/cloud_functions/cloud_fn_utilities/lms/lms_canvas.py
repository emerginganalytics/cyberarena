"""
Cloud function LMS class to create assignments
"""

from canvasapi import Canvas
from canvasapi.quiz import Quiz, QuizQuestion

from cloud_fn_utilities.lms.lms import LMS

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

    def create_quiz(self):
        questions = self.build['lms_quiz']['questions']
        points_possible = sum([q['points_possible'] for q in questions])
        quiz_data = {
            'title': f"Quiz for the Cyber Arena workout: {self.build['summary']['name']}",
            'instructions': f"The instructions to complete this quiz are here: "
                            f"{self.build['summary']['student_instructions_url']}",
            'due_at': self.build['lms_quiz']['due_at'],
            'points_possible': points_possible,
            'published': True,
            'grading_type': 'percent',
            'shuffle_answers': True
        }
        new_quiz = self.course.create_quiz(quiz_data)
        for question in questions:
            new_question = QuizQuestion()
            new_quiz.create_question(question)

    def grade_student_quiz(self):
        pass

