import os
import subprocess
import multiprocessing as mp
from time import sleep
import yaml

from install_update.operations.environment_variables import EnvironmentVariables
from install_update.operations.cyber_arena_app import CyberArenaApp
from install_update.operations.build_specification import BuildSpecification
from install_update.utilities.globals import SetupOptions, InstallSettings


__author__ = "Philip Huff"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class BulkInstallUpdate:
    DELEGATE_CMD = "gcloud iam service-accounts add-iam-policy-binding " \
                   "cyberarena-service@{project}.iam.gserviceaccount.com " \
                   "--member user:{email} --role roles/iam.serviceAccountUser"

    def __init__(self):
        print("Attempting to load the bulk settings file")
        try:
            settings = yaml.safe_load(open(InstallSettings.BULK_SETTINGS_FILENAME))
        except FileNotFoundError as e:
            print(f"The file {InstallSettings.BULK_SETTINGS_FILENAME} does not exist in the setup directory. Review "
                  f"the README file for bulk update instructions.")
            raise e
        self.deploy_functions = settings['deploy_functions']
        self.gcp_projects = settings['gcp_projects']
        response = input("Do you want to set the delegation permissions for your account on all the cloud projects "
                         "at this time? [y/N] ")
        if response.upper() == "Y":
            email = input("What email address are you using to run gcloud SDK?")
            for project in self.gcp_projects:
                ret = subprocess.run(f"gcloud config set project {project['name']}", capture_output=True, shell=True)
                print(ret.stderr.decode())
                command = self.DELEGATE_CMD.format(project=project['name'], email=email)
                ret = subprocess.run(command, capture_output=True, shell=True)
                print(ret.stderr.decode())
        print(f"Performing the functions {[x for x in self.deploy_functions]} for projects "
              f"{[x['name'] for x in self.gcp_projects]}.")

    def run(self):
        if SetupOptions.CLOUD_FUNCTION.name in self.deploy_functions:
            print(f"{SetupOptions.CLOUD_FUNCTION.name}: Beginning deployment for each specified project.")
            processes = []
            for project in self.gcp_projects:
                p = mp.Process(target=self._deploy_cloud_function, args=(project['name'], project['credential']))
                processes.append(p)
            [x.start() for x in processes]
            [x.join() for x in processes]
            print(f"{SetupOptions.CLOUD_FUNCTION.name}: Completed deployment for each specified project.")
        if SetupOptions.MAIN_APP.name in self.deploy_functions:
            print(f"{SetupOptions.MAIN_APP.name}: Beginning deployment for each specified project.")
            processes = []
            for project in self.gcp_projects:
                p = mp.Process(target=self._deploy_main_app, args=(project['name'], project['credential']))
                processes.append(p)
            [x.start() for x in processes]
            [x.join() for x in processes]
            print(f"{SetupOptions.MAIN_APP.name}: Completed deployment for each specified project.")
        if SetupOptions.ENV.name in self.deploy_functions:
            print(f"{SetupOptions.ENV.name}: Beginning deployment for each specified project. "
                  f"This process is interactive and cannot be run in parallel.")
            for project in self.gcp_projects:
                self._deploy_env(project['name'], project['credential'])
            print(f"{SetupOptions.ENV.name}: Completed deployment for each specified project.")
        if SetupOptions.BUILD_SPECS.name in self.deploy_functions:
            print(f"{SetupOptions.BUILD_SPECS.name}: Beginning deployment for each specified project.")
            processes = []
            for project in self.gcp_projects:
                p = mp.Process(target=self._deploy_build_specs(), args=(project['name'], project['credential']))
                processes.append(p)
            [x.start() for x in processes]
            [x.join() for x in processes]
            print(f"{SetupOptions.BUILD_SPECS.name}: Completed deployment for each specified project.")

    def _deploy_cloud_function(self, project_name, gcp_credential_file):
        print(f"\t{project_name}: Beginning deployment")
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = gcp_credential_file
        CyberArenaApp(suppress=True).deploy_cloud_functions()
        print(f"\t{project_name}: Completed deployment")

    def _deploy_main_app(self, project_name, gcp_credential_file):
        print(f"\t{project_name}: Beginning deployment")
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = gcp_credential_file
        CyberArenaApp(suppress=True).deploy_main_app()
        print(f"\t{project_name}: Completed deployment")

    def _deploy_env(self, project_name, gcp_credential_file):
        print(f"\t{project_name}: Beginning deployment")
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = gcp_credential_file
        EnvironmentVariables(project=project_name).run()
        print(f"\t{project_name}: Completed deployment")

    def _deploy_build_specs(self, project_name, gcp_credential_file):
        print(f"\t{project_name}: Beginning deployment")
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = gcp_credential_file
        BuildSpecification(suppress=True).run()
        print(f"\t{project_name}: Completed deployment")
