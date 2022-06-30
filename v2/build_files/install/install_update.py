from google.cloud import storage
import secrets
import os.path
import subprocess

from install.utilities.globals import InstallUpdateTypes
from install.utilities.install_update_manager import InstallUpdateManager


def main():
    project = str(input(f"What is the GCP project ID you wish to update?: "))
    subprocess.call(f"gcloud config set project {project}", shell=True)

    continue_selecting = True
    while continue_selecting:
        operation_input = "Which type of install/update would you like to perform?"
        for operation_type in InstallUpdateTypes:
            operation_input += f"\n{operation_type.value} - {operation_type.name}"
        response = int(input("Choose a number from above: "))
        InstallUpdateManager(selection=response, project=project).run()

        response = str(input("Would you like to continue performing additional installs/updates? (y/N)")).upper()
        if response == "N":
            continue_selecting = False

    region = str("us-central1")
    dns_suffix = str(input(f"Input DNS suffix for project (e.g. .example-cybergym.com): "))
    admin_email = str(input(f"Provide an email address for the super administrator of this project: "))
    api_key = str(input(f"Input the OAuth2.0 API Key for this project (from APIs and Services --> Credentials): "))



if __name__ == '__main__':
  main()