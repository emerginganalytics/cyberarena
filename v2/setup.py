import os
import subprocess
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from googleapiclient import discovery
from google.auth.exceptions import DefaultCredentialsError
from googleapiclient.errors import HttpError

from build_files.install_update.utilities.globals import SetupOptions
from build_files.install_update.utilities.setup_manager import SetupManager

__author__ = "Philip Huff"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Production"


parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
parser.add_argument("-s", "--suppress", default=None, help="Suppress input prompts and accept all defaults.")

args = vars(parser.parse_args())
suppress = args['suppress']


def main():
    bulk_update_response = str(input(f"Are you performing a bulk update?: (y/N) "))
    if bulk_update_response.upper() == "Y":
        SetupManager(selection=SetupOptions.BULK_UPDATE, project=None).run()
        exit(0)
    while True:
        project = str(input(f"What is the GCP project ID you wish to update?: "))
        ret = subprocess.run(f"gcloud config set project {project}", capture_output=True, shell=True)
        ret_msg = ret.stderr.decode()
        if 'WARNING' in ret_msg.upper():
            print(f"The following error occurred when trying to set the project:\n{ret_msg}")
        else:
            print(ret_msg)
            creds = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', None)
            if not creds:
                print(f"ERROR: gcloud CLI is not installed. Go to https://cloud.google.com/sdk/docs/install and "
                      f"follow the directions to install the CLI.")
                exit(1)
            else:
                while True:
                    response = str(input(f"Your current GCP credentials are set to: {creds}. Are these associated "
                                         f"with the project {project}? (Y/n) "))
                    if response.upper() == "N":
                        cred_update = str(input(f"What is the path to your credentials for {project}? "))
                        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = cred_update
                    if test_gcp_credentials(project):
                        break
                    else:
                        print(f"Error: the GCP credentials provided did not work for connecting to {project}")

            break
    operation_prompt = "Select an operation to perform?"
    for option in SetupOptions:
        operation_prompt += f"\n[{option.value}] - {option.description}"
    operation_prompt += "\nSelection? "

    while True:
        response = int(input(operation_prompt))
        if SetupOptions(response) == SetupOptions.EXIT:
            break
        elif response > len(SetupOptions):
            print(f"Invalid selection. Select an option 0-{len(SetupOptions)}")
        else:
            SetupManager(selection=SetupOptions(response), project=project).run()
            response = str(input("Would you like to perform additional setup tasks? (y/N) ")).upper()
            if not response or response == "N":
                break


def test_gcp_credentials(project):
    try:
        service = discovery.build('compute', 'v1')
        service.instances().list(project=project, zone="us-central1-b").execute()
        return True
    except (DefaultCredentialsError, HttpError) as err:
        return False


if __name__ == '__main__':
    main()
