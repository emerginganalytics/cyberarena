import copy
from app_utilities.gcp.datastore_manager import DataStoreManager
from app_utilities.globals import DatastoreKeyTypes, CipherModes, Algorithms


class AssessmentManager:
    def __init__(self, build_id, build=None):
        self.build_id = build_id
        self.ds = DataStoreManager(key_type=DatastoreKeyTypes.WORKOUT, key_id=build_id)
        self.build = build if build else self.ds.get()

    def evaluate(self, question_id, submission):
        update = self._evaluate(question_id, submission)
        if update:
            self.ds.put(self.build)
        return update, self._clean()

    def _evaluate(self, question_id, submission):
        """Checks submitted answer for question with matching question_id and
        returns True or False"""
        if escape_room := self.build.get('escape_room', None):
            assessment = self.build['escape_room']['puzzles']
        else:
            assessment = self.build['assessment']['questions']
        for question in assessment:
            if question['id'] == question_id:
                if str(submission) == question['answer']:
                    question['complete'] = True
                    return True
        return False

    def _clean(self):
        """
            Removes the answers from the returning assessment object
        """
        if escape_room := self.build.get('escape_room', None):
            assessment = copy.deepcopy(self.build['escape_room']['puzzles'])
        else:
            assessment = copy.deepcopy(self.build['assessment']['questions'])
        for question in assessment:
            question['answer'] = ''
        return assessment
