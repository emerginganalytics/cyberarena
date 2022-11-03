
class SQLMap:
    def __init__(self, rhost, args):
        self.module = 'sqlmap'
        self.rhost = rhost
        self.args = args

    def build_attack(self):
        attack = f'{self.module} -u {self.rhost}'
