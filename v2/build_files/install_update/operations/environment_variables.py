import subprocess
from enum import Enum
from google.cloud import runtimeconfig
from googleapiclient import discovery

from install_update.utilities.globals import ShellCommands


class EnvironmentVariables:
    COMMAND = "gcloud beta runtime-config configs variables set \"{variable}\" \"{value}\" --config-name \"cybergym\""
    DEFAULT_REGION = "us-central1"
    DEFAULT_ZONE = "us-central1-a"

    def __init__(self, project, suppress=True):
        self.project = project
        self.suppress = suppress
        self.service = discovery.build('compute', 'v1')
        runtimeconfig_client = runtimeconfig.Client()
        self.myconfig = runtimeconfig_client.config('cybergym')

    def run(self):
        reply = str(input(f"Do you want to update a specific environment variable or ALL environmental variables "
                          f"for {self.project}? [s]pecific/[A]ll")).upper()
        if reply in ["S", "SPECIFIC"]:
            while True:
                var = str(input(f"Which variable do you want to update?"))
                self._set_variable(var)
                response = str(input("Would you like to set another variable? (y/N)")).upper()
                if not response or response == "N":
                    break
        else:
            self._set_variable("project", self.project)
            self._set_region()
            self._set_zone()
            for var in self.Variables:
                self._set_variable(var)

    def _set_variable(self, var, new_value=None):
        current_val = self.myconfig.get_variable(var)
        current_val = current_val.value.decode("utf-8") if current_val else "EMPTY"
        if current_val == new_value:
            print("Given value is the same as the set value. No change is needed.")
            return
        elif new_value:
            prompt = f"The current value of {var} is {current_val}. Do you wish to set it to {new_value}? (Y/n)"
        else:
            prompt = f"The current value of {var} is {current_val}. Do you wish to set it? (Y/n)"
        reply = str(input(prompt)).upper()
        if not reply or reply == "Y":
            if not new_value:
                new_value = str(input(f"What value would you like to set for {var}?"))
            command = self.COMMAND.format(variable=var, value=new_value)
            ret = subprocess.run(command, capture_output=True, shell=True)
            print(ret.stderr.decode())

    def _set_region(self):
        response = self.service.regions().list(project=self.project).execute()
        region_options = {}
        options_string = "\n"
        for i, region_option in enumerate(response['items']):
            region_options[i] = region_option['name']
            options_string += f"[{i}] {region_option['name']}\n"

        reply = input(f"Region options:\n{options_string}Enter the number beside the region in which you like to "
                      f"run the Cyber Arena? Default is {self.DEFAULT_REGION}")
        region = region_options[int(reply)] if reply.isnumeric() else self.DEFAULT_REGION
        self._set_variable("region", region)

    def _set_zone(self):
        response = self.service.zones().list(project=self.project).execute()
        zone_options = {}
        options_string = "\n"
        for i, zone_option in enumerate(response['items']):
            zone_options[i] = zone_option['name']
            options_string += f"[{i}] {zone_option['name']}\n"

        reply = input(f"Zone options:\n{options_string}Enter the number beside the zone in which you like to "
                      f"run the Cyber Arena? Default is {self.DEFAULT_ZONE}")
        zone = zone_options[int(reply)] if reply.isnumeric() else self.DEFAULT_ZONE
        self._set_variable("zone", zone)

    class Variables(str, Enum):
        DNS_SUFFIX = "dns_suffix"
        SCRIPT_REPOSITORY = "script_repository"
        API_KEY = "api_key"
        MAIN_APP_URL = "main_app_url"
        ADMIN_EMAIL = "admin_email"