"""
Cloud function LMS class to create assignments
"""
import json
from canvasapi import Canvas
from canvasapi.quiz import Quiz, QuizQuestion

from cloud_fn_utilities.gcp.cloud_env import CloudEnv
from cloud_fn_utilities.lms.lms import LMS

__author__ = "Philip Huff"
__copyright__ = "Copyright 2023, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff"]
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class CanvasConstants:
    class Questions:
        class Types:
            SHORT_ANSWER = 'short_answer_question'
            ESSAY_QUESTION = 'essay_question'
            FILE_UPLOAD_QUESTION = 'file_upload_question'


class LMSCanvas(LMS):
    def __init__(self, url, api_key, course_code, build, env_dict=None):
        super().__init__(url, api_key, course_code, build)
        self.env = CloudEnv(env_dict=env_dict) if env_dict else CloudEnv()
        self.canvas = Canvas(self.url, self.api_key)
        self.course = self.canvas.get_course(self.course_code)
        self.class_list = self.course.get_users(enrollment_type=['student'])

    def get_class_list(self):
        students = []
        for student in self.class_list:
            students.append({
                    'email': student.email,
                    'name': student.name
                })
        return students

    def create_quiz(self, delete_existing_quizzes=True):
        questions = self.build['lms_quiz']['questions']
        points_possible = sum([q['points_possible'] for q in questions])
        quiz_name = f"Quiz for the Cyber Arena workout: {self.build['summary']['name']}"
        if delete_existing_quizzes:
            self.delete_quiz_by_name(quiz_name)
        quiz_data = {
            'title': quiz_name,
            'instructions': f"Your lab is available at {self.env.main_app_url_v2}/student/join. Use the join code "
                            f"{self.build.get('join_code', None)} and the email address used to login to this site. "
                            f"The instructions to complete this quiz are here: "
                            f"{self.build['summary']['student_instructions_url']}",
            'due_at': self.build['lms_quiz']['due_at'],
            'points_possible': float(points_possible),
            'published': True,
            'grading_type': 'percent',
            'shuffle_answers': True,
            'assignees': [{'id': x.id, 'type': 'user'} for x in self.class_list]
        }
        new_quiz = self.course.create_quiz(quiz_data)
        question_ids = []
        for question in json.loads(json.dumps(questions)):
            question_data = {
                'question_name': question.get('question_name', None),
                'question_text': question.get('question_text', None),
                'question_type': question.get('question_type', CanvasConstants.Questions.Types.SHORT_ANSWER),
                'points_possible': float(question.get('points_possible', 1)),
                'answers': question.get('answers', None)
            }
            question = new_quiz.create_question(question=question_data)
            question_ids.append(question.id)
        self._store_quiz_identifiers(quiz_id=new_quiz.id, question_ids=question_ids)
        return new_quiz

    def get_updated_build(self):
        """
        It's dangerous to save a Datastore Entity inside a class. Otherwise, it could be overwritten by the calling
        function.
        Returns:

        """
        return self.build

    def delete_quiz_by_name(self, quiz_name: str):
        assigned_quizzes = self.course.get_assignments()
        for quiz in assigned_quizzes:
            if quiz.name == quiz_name:
                quiz.delete()

    def _store_quiz_identifiers(self, quiz_id: int, question_ids: list):
        self.build['lms_quiz']['quiz_id'] = quiz_id
        for i, question in enumerate(self.build['lms_quiz']['questions']):
            question['question_id'] = question_ids[i]
