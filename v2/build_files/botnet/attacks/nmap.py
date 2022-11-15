class Nmap:
    def __init__(self, rhost, args):
        self.module = 'nmap'
        self.rhost = rhost
        self.args = args
        self.attack = f'{self.module} {self.rhost}'

    def build_attack(self):
        if 'rport' in self.args:
            self.attack = f'{self.attack} -p {self.args["rport"]}'
        return self.attack
