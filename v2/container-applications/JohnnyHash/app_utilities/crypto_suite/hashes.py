import io
import hashlib
import random
from hashlib import md5
from enum import Enum
from app_utilities.gcp.datastore_manager import DataStoreManager
from app_utilities.globals import DatastoreKeyTypes


class Hashes:
    def __init__(self, build_id=None):
        self.build_id = build_id
        self.ds = DataStoreManager(key_type=DatastoreKeyTypes.WORKOUT.value, key_id=self.build_id)
        if self.build_id:
            self.build = self.ds.get()
        self.passkey = dict()
        self.update = False

    def _generate_md5_passkey(self):
        password = {'rand_pass': '', 'hash': '',}
        # Password format {str}{int}. If len(str) < 8, {int}{str}{int}
        str_list = [
            'Ornn', 'Hak5', 'Hacking',
            'BlackHatPython', 'SpiesAmongUs', '9999',
            '1994', '5', '7', '33', '19', '2020', '1234','0000'
        ]
        password['rand_pass'] = random.choice(str_list[0:5])
        password['rand_pass'] += random.choice(str_list[6:14])
        if len(password['rand_pass']) < 8:
            password['rand_pass'] = random.choice(str_list[6:14]) + password['rand_pass']
        password['hash'] = md5(str(password['rand_pass']).encode('UTF-8')).hexdigest()
        self.passkey = password

    def _set_md5_passkey(self, question, question_id):
        """
        Takes the input question_id and verifies that a hash has already been generated for
        that question. If no hash is found, the function will generate a random hash
        and update the datastore record.
        :param question: dict()
        :param question_id: Unique Question Identifier to check for generated hash
        :return: Bool(False if already populated or question_id doesn't match)
        """
        if question['id'] == str(question_id):
            if question['question'] == '':  # question isn't populated; Generate key
                self._generate_md5_passkey()
                question['question'] = self.passkey['hash']
                question['answer'] = self.passkey['rand_pass']
                self.ds.put(self.build)
                return True
        return False

    def complete(self, build_id, workout_info, question_id):
        if workout_info.get('escape_room', None):
            for puzzle in workout_info['escape_room']['puzzles']:
                if puzzle['id'] == question_id:
                    puzzle['correct'] = True
                    break
        elif workout_info.get('assessment', None):
            for question in workout_info['assessment']['questions']:
                if question_id == question['id']:
                    question['complete'] = True
                    break
        else:
            raise ValueError(f'Question Not Found with ID :: {question_id}')
        # Update the Workout
        DataStoreManager(key_type=DatastoreKeyTypes.WORKOUT.value, key_id=build_id).put(workout_info)
        # self.ds.put(workout_info)

    def set_md5_hash(self, question_id=None):
        if not self.build:
            raise ValueError(f'No build found with build_id {self.build_id}')
        if self.build and question_id:
            if self.build.get('escape_room', None):
                for puzzle in self.build['escape_room']['puzzles']:
                    if self._set_md5_passkey(puzzle, question_id):
                        break
            elif self.build.get('assessment', None):
                for question in self.build['assessment']['questions']:
                    if self._set_md5_passkey(question, question_id):
                        break
            return self.passkey
        else:
            if self.build.get('escape_room', None):
                for puzzle in self.build['escape_room']['puzzles']:
                    if puzzle['entry_name'] == 'Johnny Hash':
                        if self._set_md5_passkey(puzzle, puzzle['id']):
                            break
            if self.build.get('assessment', None):
                for question in self.build['assessment']['questions']:
                    if self._set_md5_passkey(question, question['id']):
                        break
            return self.passkey

    @staticmethod
    def validate_hashes_from_file(input_file):
        if input_file.filename == '':
            return HashErrors.EMPTY_FILE
        raw_input = io.StringIO(input_file.stream.read().decode("UTF8"), newline=None)
        passwords = raw_input.read().split('\n')
        hashes = []
        for password in passwords:
            hashes.append({
                'plaintext': password,
                'hash': hashlib.md5(password.encode('utf-8')).hexdigest()
            })
        return hashes

    @staticmethod
    def get_password(workout_info, question_id):
        if workout_info.get('escape_room', None):
            for puzzle in workout_info['escape_room']['puzzles']:
                if puzzle['id'] == question_id:
                    return puzzle['answer']
        elif workout_info.get('assessment', None):
            for question in workout_info['assessment']['questions']:
                if question['id'] == question_id:
                    return question['answer']
        return False

    @staticmethod
    def get_question_id(workout_info):
        if workout_info.get('escape_room', None):
            for puzzle in workout_info['escape_room']['puzzles']:
                if puzzle['entry_name'] == 'Johnny Hash':
                    return puzzle['id']
        if workout_info.get('assessment', None):
            for question in workout_info['assessment']['questions']:
                return question['id']


class HashErrors:
    NO_FILE_SUBMITTED = 'You must choose a file to upload'
    EMPTY_FILE = 'You must choose a file to upload'

# [ eof ]
