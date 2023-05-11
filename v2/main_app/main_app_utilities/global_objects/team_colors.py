
class TeamColors:
	def __init__(self, build_count):
		self.build_count = build_count
		self.colors = [
			('#9CAF88', 'black'), ('#ff99cc', 'white'),
			('#ffff00', 'black'), ('#808080', 'white'),
			('#245C4E', 'white'), ('#2b5b84', 'white'),
			('#6e2639', 'white'),
		]

	def get(self):
		return [self.colors[i] for i in range(self.build_count)]
