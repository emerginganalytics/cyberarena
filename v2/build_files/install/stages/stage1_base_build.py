import subprocess
from enum import Enum

from install.utilities.globals import ShellCommands


class BaseBuild:
    def __init__(self, project, suppress=True):
        self.project = project
        self.suppress = suppress

    def run(self):
        confirmation = str(input("Do you want to enable the necessary APIs at this time? (Y/n): ")).upper() \
            if not self.suppress else "Y"
        if confirmation == "Y":
            commands = '; '.join([x.value for x in ShellCommands.EnableAPIs])
            ret = subprocess.call(commands, stdout=True, shell=True)
            print(ret.stdout.decode())

        confirmation = str(input("Do you want to create the service account at this time? (Y/n): ")).upper() \
            if not self.suppress else "Y"
        if confirmation == "Y":
            commands = '; '.join([x.value for x in ShellCommands.ServiceAccount])
            commands = commands.format(project=self.project)
            ret = subprocess.call(commands, stdout=True, shell=True)
            print(ret.stdout.decode())

        confirmation = str(input("Do you want to create pubsub topics at this time? (Y/n): ")).upper() \
            if not self.suppress else "Y"
        if confirmation == "Y":
            commands = '; '.join([x.value for x in ShellCommands.PubSubTopics])
            ret = subprocess.call(commands, stdout=True, shell=True)
            print(ret.stdout.decode())
