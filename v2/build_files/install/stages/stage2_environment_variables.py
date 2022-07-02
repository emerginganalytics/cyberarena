import subprocess
from enum import Enum
from google.cloud import runtimeconfig

from install.utilities.globals import ShellCommands


class EnvironmentVariables:
    COMMAND = "gcloud beta runtime-config configs variables set '{variable}' {value} --config-name 'cybergym'"

    def __init__(self, project, suppress=True):
        self.project = project
        self.suppress = suppress
        runtimeconfig_client = runtimeconfig.Client()
        self.myconfig = runtimeconfig_client.config('cybergym')

    def run(self):
        continue_setting = True
        while continue_setting:
            reply = str(input(f"Do you want to update a specific environment variable or ALL environmental variables for "
                      f"{self.project}? [s]pecific/[A]ll")).upper()
            if reply == "S" or "SPECIFIC":
                var = str(input(f"Which variable do you want to update?"))
                self._set_variable(var)
                response = str(
                    input("Would you like to set another variable? (y/N)")).upper()
                if response == "N":
                    continue_setting = False
            else:
                continue_setting = False
                for var in self.Variables:
                    self._set_variable(var)

    def _set_variable(self, var):
        current_val = self.myconfig.get_variable(var)
        current_val = current_val.value.decode("utf-8") if current_val else "EMPTY"
        reply = str(input(f"The current value of {var} is {current_val}. Do you wish to set it? (Y/n)")).upper()
        if reply == "Y":
            val = str(input(f"What value would you like to set for {var}?"))
            command = self.COMMAND.format(variable=var, value=val)
            ret = subprocess.call(command, stdout=True, shell=True)
            print(ret.stdout.decode())

    class Variables(str, Enum):
        PROJECT = "project"
        REGION = "region"
        ZONE = "zone"
        DNS_SUFFIX = "dns_suffix"
        SCRIPT_REPOSITORY = "script_repository"
        API_KEY = "api_key"
        MAIN_APP_URL = "main_app_url"
        ADMIN_EMAIL = "admin_email"