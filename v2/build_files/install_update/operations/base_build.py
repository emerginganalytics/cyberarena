import subprocess
from googleapiclient import discovery

from install_update.utilities.globals import ShellCommands

__author__ = "Philip Huff"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class BaseBuild:
    def __init__(self, project, suppress=False):
        self.project = project
        self.suppress = suppress
        self.service = discovery.build('iam', 'v1')

    def run(self):
        confirmation = str(input("Do you want to enable the necessary APIs at this time? (Y/n): ")).upper() \
            if not self.suppress else "Y"
        if confirmation == "Y":
            for item in ShellCommands.EnableAPIs:
                print(f"Running: {item.value}")
                ret = subprocess.run(item.value, capture_output=True, shell=True)

        confirmation = str(input("Do you want to create the service account at this time? (Y/n): ")).upper() \
            if not self.suppress else "Y"
        if confirmation == "Y":
            name = f'projects/{self.project}'
            response = self.service.projects().serviceAccounts().list(name=name).execute()
            service_account_exists = False
            for service_account in response.get('accounts', []):
                if service_account.get('displayName', None) == "cyberarena-service":
                    print("Service account already exists. Skipping configuration")
                    service_account_exists = True
                    break
            if not service_account_exists:
                for item in ShellCommands.ServiceAccount:
                    command = item.value.format(project=self.project)
                    print(f"Running: {command}")
                    ret = subprocess.run(command, capture_output=True, shell=True)
                    print(ret.stderr.decode())

        confirmation = str(input("Do you want to create pubsub topics at this time? (Y/n): ")).upper() \
            if not self.suppress else "Y"
        if confirmation == "Y":
            for item in ShellCommands.PubSubTopics:
                print(f"Running: {item.value}")
                ret = subprocess.run(item.value, capture_output=True, shell=True)
                print(ret.stderr.decode())
