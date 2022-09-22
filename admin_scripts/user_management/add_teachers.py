from google.cloud import datastore
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

from script_utilities.gcp_credential_manager import GCPCredentialManager

__author__ = "Philip Huff"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Production"


# Parse command line arguments
parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
parser.add_argument("-t", "--teachers", default=None, help="comma separated list of teachers to authorize for "
                                                           "a project")
parser.add_argument("-p", "--project", default=None, help="The project to use for adding teachers")

args = vars(parser.parse_args())

# Set up parameters
teachers = args.get('teachers', [])
project = args.get('project', None)


class Teacher:
    def __init__(self):
        self.ds_client = datastore.Client()
        self.teachers = [x.strip() for x in teachers.split(",")]

    def add(self):
        admin_info = self.ds_client.get(self.ds_client.key('cybergym-admin-info', 'cybergym'))
        admin_info['authorized_users'] += self.teachers
        self.ds_client.put(admin_info)


if __name__ == "__main__":
    if not teachers:
        teachers = str(input(f"Enter a comma separated list of teachers to add:"))

    if not project:
        project = str(input(f"In which project do you want to add the teachers?"))

    GCPCredentialManager(project=project).check_gcp_credentials()
    Teacher().add()
