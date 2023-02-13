import subprocess
from enum import Enum
from google.cloud import runtimeconfig
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


class EnvironmentVariables:
    COMMAND = "gcloud beta runtime-config configs variables set \"{variable}\" \"{value}\" --config-name \"cybergym\""
    DEFAULT_REGION = "us-central1"
    DEFAULT_ZONE = "us-central1-a"
    VARIABLES = ['dns_suffix', 'api_key', 'main_app_url', 'main_app_url_v2', 'admin_email', 'guac_password',
                 'project_number', 'sql_password', 'sql_ip']

    def __init__(self, project):
        self.project = project
        self.service = discovery.build('compute', 'v1')
        runtimeconfig_client = runtimeconfig.Client()
        self.myconfig = runtimeconfig_client.config('cybergym')

    def run(self):
        reply = str(input(f"Do you want to update a specific environment variable or ALL environmental variables "
                          f"for {self.project}? [s]pecific/[A]ll")).upper()
        if reply in ["S", "SPECIFIC"]:
            while True:
                var = str(input(f"Which variable do you want to update?"))
                self.set_variable(var)
                response = str(input("Would you like to set another variable? (y/N)")).upper()
                if not response or response == "N":
                    break
        else:
            self.set_variable("project", self.project)
            self._set_region()
            self._set_zone()
            for var in self.VARIABLES:
                self.set_variable(var)

    def set_variable(self, var, new_value=None):
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
        self.set_variable("region", region)

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
        self.set_variable("zone", zone)

    class Variables(str, Enum):
        DNS_SUFFIX = "dns_suffix"
        API_KEY = "api_key"
        MAIN_APP_URL = "main_app_url"
        MAIN_APP_URL_V2 = "main_app_url_v2"
        ADMIN_EMAIL = "admin_email"
        SQL_IP = "sql_ip"
        SQL_PASSWORD = "sql_password"
