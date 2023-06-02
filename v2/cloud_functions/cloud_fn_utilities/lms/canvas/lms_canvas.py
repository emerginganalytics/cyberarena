"""
Cloud function LMS class to create assignments
"""
import json
from canvasapi import Canvas

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
            FILL_IN_MULTIPLE_BLANKS = 'fill_in_multiple_blanks_question'
            MULTIPLE_ANSWERS = 'multiple_answers_question'
            MULTIPLE_CHOICE = 'multiple_choice_question'
            BOOLEAN = 'true_false_question'


class LMSCanvas(LMS):
    def __init__(self, url, api_key, course_code, build, env_dict=None):
        super().__init__(url, api_key, course_code, build)
        self.env = CloudEnv(env_dict=env_dict) if env_dict else CloudEnv()
        self.canvas = Canvas(self.url, self.api_key)
        self.course = self.canvas.get_course(self.course_code)
        self.class_list = self.course.get_users(enrollment_type=['student'])

    def get_class_list(self, suppress_logs=False):
        students = []
        for student in self.class_list:
            try:
                students.append({
                        'email': student.email,
                        'name': student.name
                    })
            except AttributeError:
                if hasattr(student, 'name') and not suppress_logs:
                    self.logger.warning(f"Email does not exist for {student.name} and a workout will not be created "
                                        f"for them!")
                elif not suppress_logs:
                    self.logger.warning(f"Error when trying to enumerate class list. Student record has no name!")
        return students

    def create_quiz(self, delete_existing_quizzes=True):
        questions = self.build['lms_quiz']['questions']
        quiz_name = f"Quiz for the Cyber Arena workout: {self.build['summary']['name']}"
        if delete_existing_quizzes:
            self.delete_quiz_by_name(quiz_name)
        description = self._get_description()
        quiz_data = {
            'title': quiz_name,
            'description': description,
            'due_at': self.build['lms_quiz']['due_at'],
            'show_correct_answers': False,
            'allowed_attempts': -1,
            'published': False,
            'grading_type': 'percent',
            'shuffle_answers': True,
            'assignees': [{'id': x.id, 'type': 'user'} for x in self.class_list]
        }
        new_quiz = self.course.create_quiz(quiz_data)
        question_ids = []
        total_points = 0
        for question in json.loads(json.dumps(questions)):
            points_possible = float(question.get('points_possible', 1))
            question_data = {
                'question_name': question.get('question_name', None),
                'question_text': question.get('question_text', None),
                'question_type': question.get('question_type', CanvasConstants.Questions.Types.SHORT_ANSWER),
                'points_possible': points_possible,
                'answers': question.get('answers', None)
            }
            question_obj = new_quiz.create_question(question=question_data)
            question_ids.append(question_obj.id)
            if not question.get('bonus', None):
                total_points += points_possible
        self._store_quiz_identifiers(quiz_key=new_quiz.id, question_ids=question_ids)
        new_quiz.edit(quiz={'points_possible': total_points, 'published': True})
        return new_quiz

    def get_updated_build(self):
        """
        It's dangerous to save a Datastore Entity inside a class. Otherwise, it could be overwritten by the calling
        function.
        Returns: None

        """
        return self.build

    def delete_quiz_by_name(self, quiz_name: str):
        assigned_quizzes = self.course.get_assignments()
        for quiz in assigned_quizzes:
            if quiz.name == quiz_name:
                quiz.delete()

    def _store_quiz_identifiers(self, quiz_key: int, question_ids: list):
        self.build['lms_quiz']['quiz_key'] = quiz_key
        for i, question in enumerate(self.build['lms_quiz']['questions']):
            question['question_key'] = question_ids[i]

    def _get_description(self):
        description = f"Your lab is available at " \
                      f"<a href=https://{self.env.main_app_url_v2}/student/join target=_blank>Cyber Arena</a>. " \
                      f"Use the join code {self.build.get('join_code', None)} and the email address used to login " \
                      f"to this site. "
        if student_instructions_url := self.build['summary'].get('student_instructions_url', None):
            description = f"{description}The instructions to complete this quiz are here: " \
                          f"<a href={student_instructions_url} target=_blank>" \
                          f"Lab Instructions.</a>"
        return f"<p>{description}</p>"
