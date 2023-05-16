
from v2.main_app.main_app_utilities.globals import DatastoreKeyTypes, PubSub
from v2.main_app.main_app_utilities.gcp.datastore_manager import DataStoreManager


class TestEscapeRoom:
	def __init__(self, build_id):
		self.build_id = build_id
		self.ds = DataStoreManager(key_type=DatastoreKeyTypes.WORKOUT, key_id=self.build_id)

	def mark_question_as_complete(self):
		build = self.ds.get()
		print('Escape Room Question Evaluator')
		print('Input | Question')
		puzzles = dict()
		count = 0
		for puzzle in build['escape_room']['puzzles']:
			puzzles[count] = puzzle['id']
			print(f'[{count}] - {puzzle["name"]}')
			count += 1

		question = int(input('Select a puzzle to mark as complete: '))
		question_id = puzzles.get(question, None)
		if not question_id:
			print('Invalid menu selection given!')
			raise ValueError
		for puzzle in build['escape_room']['puzzles']:
			if puzzle['id'] == question_id:
				puzzle['correct'] = True
				print(f'Marking question {question} as correct')
				self.ds.put(build)
				break

