import os
import subprocess
from googleapiclient import discovery
from google.auth.exceptions import DefaultCredentialsError
from googleapiclient.errors import HttpError

__author__ = "Philip Huff"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class GCPCredentialManager:
    def __init__(self):
        pass

    @staticmethod
    def check_gcp_credentials():
        while True:
            project = str(input(f"What is the GCP project ID you wish to use?: "))
            ret = subprocess.run(f"gcloud config set project {project}", capture_output=True, shell=True)
            ret_msg = ret.stderr.decode()
            if 'WARNING' in ret_msg.upper():
                print(f"The following error occured when trying to set the project:\n{ret_msg}")
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
                                             f"with the project {project}? (Y/n)"))
                        if response.upper() == "N":
                            cred_update = str(input(f"What is the path to your credentials for {project}?"))
                            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = cred_update
                        if GCPCredentialManager._test_gcp_credentials(project):
                            break
                        else:
                            print(f"Error: the GCP credentials provided did not work for connecting to {project}")

                break

    @staticmethod
    def _test_gcp_credentials(project):
        try:
            service = discovery.build('compute', 'v1')
            service.instances().list(project=project, zone="us-central1-b").execute()
            return True
        except (DefaultCredentialsError, HttpError) as err:
            return False
