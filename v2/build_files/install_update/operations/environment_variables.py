from enum import Enum
from googleapiclient import discovery
import pytz

from cloud_fn_utilities.gcp.datastore_manager import DataStoreManager
from cloud_fn_utilities.globals import DatastoreKeyTypes
from main_app_utilities.gcp.arena_authorizer import ArenaAuthorizer

__author__ = "Philip Huff"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class EnvironmentVariables:
    DEFAULT_REGION = "us-central1"
    DEFAULT_ZONE = "us-central1-a"
    DEFAULT_TIMEZONE = "America/Chicago"
    VARIABLES = ['dns_suffix', 'dnszone', 'api_key', 'main_app_url', 'main_app_url_v2', 'admin_email',
                 'guac_db_password', 'project_number', 'max_workspaces', 'sendgrid_api_key', 'shodan_api_key']

    def __init__(self, project):
        self.project = project
        self.service = discovery.build('compute', 'v1')
        self.ds = DataStoreManager(key_type=DatastoreKeyTypes.ADMIN_INFO, key_id='cyberarena')
        self.env = self.ds.get()

    def run(self):
        reply = str(input(f"Do you want to update a specific environment variable or ALL environmental variables "
                          f"for {self.project}? [s]pecific/[A]ll")).upper()
        if reply in ["S", "SPECIFIC"]:
            while True:
                var = str(input(f"Which variable do you want to update?"))
                self.set_variable(var)
                response = str(input("Would you like to set another variable? (y/N)")).upper()
                if not response or response == "N":
                    self.ds.put(self.env)
                    break
        else:
            self.set_variable("project", self.project)
            self._set_region()
            self._set_zone()
            self._set_timezone()
            for var in self.VARIABLES:
                self.set_variable(var)

    def set_variable(self, var, new_value=None):
        current_val = self.env.get(var, None)
        if current_val and current_val == new_value:
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
            self.env[var] = new_value
            if var == 'admin_email':
                ArenaAuthorizer().add_user(
                    email=new_value.lower(), admin=True,
                    instructor=True, student=True
                )
            self.ds.put(self.env)

    def remove_variable(self):
        current_vars = list(self.env.items())
        print('Environment Variables::')
        for i in enumerate(current_vars):
            print(f'\t[{i[0]}] {current_vars[i[0]][0]}')

        idx = int(input('Which variable would you like to remove? '))
        var = current_vars[idx]
        if var[0] in self.env:
            del self.env[var[0]]
            print(f'Removed {var[0]} from environment')
            self.ds.put(self.env)
        else:
            print(f'Could not find variable with name: {var[0]}')

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

    def _set_timezone(self):
        reply = input(f"What timezone do you want to set for the project? Use the IANA Timezone identifier. "
                      f"The default is {self.DEFAULT_TIMEZONE}")
        timezone = reply if reply else self.DEFAULT_TIMEZONE
        try:
            pytz.timezone(timezone)
        except pytz.UnknownTimeZoneError:
            print(f"Unknown timezone entered! Setting the timezone to {self.DEFAULT_TIMEZONE}")
            timezone = self.DEFAULT_TIMEZONE
        self.set_variable("timezone", timezone)

    class Variables(str, Enum):
        DNS_SUFFIX = "dns_suffix"
        API_KEY = "api_key"
        MAIN_APP_URL = "main_app_url"
        MAIN_APP_URL_V2 = "main_app_url_v2"
        ADMIN_EMAIL = "admin_email"
