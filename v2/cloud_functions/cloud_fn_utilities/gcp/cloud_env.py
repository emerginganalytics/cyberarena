import random
import time
from google.cloud import runtimeconfig
from googleapiclient.errors import HttpError

from cloud_fn_utilities.gcp.datastore_manager import DataStoreManager
from cloud_fn_utilities.globals import DatastoreKeyTypes

__author__ = "Philip Huff"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff", 'Andrew Bomberger']
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class CloudEnv:
    MAX_TRIES = 5

    def __init__(self, env_dict=None):
        """
        Pull all the environment variables. If an HTTP error occurs because of too many requests, then back off a few
        seconds each time.
        """
        self.ds = DataStoreManager(key_type=DatastoreKeyTypes.ADMIN_INFO, key_id='cyberarena')
        self.env_dict = env_dict if env_dict else self.ds.get()
        if self.env_dict:
            self.admin_email = self.env_dict['admin_email']
            # GCP Project Variables
            self.project = self.env_dict['project']
            self.project_number = self.env_dict.get('project_number', None)
            self.region = self.env_dict['region']
            self.zone = self.env_dict['zone']
            self.timezone = self.env_dict.get('timezone', 'America/Chicago')
            self.custom_dnszone = self.env_dict.get('custom_dnszone', None)
            self.dnszone = self.env_dict['dnszone']
            # Cyber Arena Variables
            self.main_app_url = self.env_dict['main_app_url']
            self.main_app_url_v2 = self.env_dict['main_app_url_v2']
            self.dns_suffix = self.env_dict['dns_suffix']
            self.max_workspaces = self.env_dict['max_workspaces']
            self.spec_bucket = self.env_dict['spec_bucket']
            self.student_instructions_url = self.env_dict['student_instructions_url']
            self.teacher_instructions_url = self.env_dict['teacher_instructions_url']
            # Database Variables
            self.guac_db_password = self.env_dict['guac_db_password']
            self.sql_ip = self.env_dict.get('sql_ip', None)
            self.sql_password = self.env_dict.get('sql_password', None)
            # API Keys
            self.api_key = self.env_dict['api_key']
            self.sendgrid_api_key = self.env_dict.get('sendgrid_api_key', None)
            self.shodan_api_key = self.env_dict.get('shodan_api_key', None)
        else:
            # Env dictionary wasn't passed in or obj doesn't exist in Datastore
            self.load_from_runtimeconfig()

    def load_from_runtimeconfig(self):
        runtimeconfig_client = runtimeconfig.Client()
        myconfig = runtimeconfig_client.config('cybergym')
        i = 0
        while i < self.MAX_TRIES:
            try:
                self.project = myconfig.get_variable('project').value.decode("utf-8")
                self.project_number = myconfig.get_variable('project_number').value.decode('utf-8')
                self.region = myconfig.get_variable('region').value.decode("utf-8")
                self.zone = myconfig.get_variable('zone').value.decode("utf-8")
                self.dns_suffix = myconfig.get_variable('dns_suffix').value.decode("utf-8")
                self.api_key = myconfig.get_variable('api_key').value.decode("utf-8")
                self.custom_dnszone = myconfig.get_variable('dnszone')
                if self.custom_dnszone is not None:
                    self.dnszone = self.custom_dnszone.value.decode("utf-8")
                else:
                    self.dnszone = 'cybergym-public'
                student_instructions_url = myconfig.get_variable('student_instructions_url')
                self.student_instructions_url = student_instructions_url.value.decode(
                    "utf-8") if student_instructions_url else \
                    'https://storage.googleapis.com/student_workout_instructions_ualr-cybersecurity/'
                teacher_instructions_url = myconfig.get_variable('teacher_instructions_url')
                self.teacher_instructions_url = teacher_instructions_url.value.decode(
                    "utf-8") if teacher_instructions_url else \
                    'https://storage.googleapis.com/teacher_workout_instructions_ualr-cybersecurity/'
                self.main_app_url = myconfig.get_variable('main_app_url').value.decode("utf-8")
                main_app_url_v2 = myconfig.get_variable('main_app_url_v2')
                if main_app_url_v2:
                    self.main_app_url_v2 = main_app_url_v2.value.decode("utf-8")
                else:
                    self.main_app_url_v2 = self.main_app_url
                self.guac_db_password = myconfig.get_variable('guac_password').value.decode("utf-8")
                self.spec_bucket = self.project + '_build-specs'
                self.admin_email = myconfig.get_variable('admin_email').value.decode("utf-8")
                max_workspaces = myconfig.get_variable('max_workspaces')
                self.max_workspaces = int(max_workspaces.value.decode("utf-8")) if max_workspaces else 100
                self.auth_config = {
                    'api_key': self.api_key,
                    'auth_domain': str(self.project + ".firebaseapp.com"),
                    'project_id': self.project
                }
                sendgrid_api_key = myconfig.get_variable('SENDGRID_API_KEY', None)
                if sendgrid_api_key:
                    self.sendgrid_api_key = sendgrid_api_key.value.decode('utf-8')
                if shodan_api_key := myconfig.get_variable('shodan_api_key', None):
                    self.shodan_api_key = shodan_api_key.value.decode('utf-8')
                timezone = myconfig.get_variable('timezone', None)
                if timezone:
                    self.timezone = timezone.value.decode('utf-8')
                else:
                    self.timezone = 'America/Chicago'
                sql_ip = myconfig.get_variable('sql_ip')
                self.sql_ip = sql_ip.value.decode("utf-8") if sql_ip else None
                sql_password = myconfig.get_variable('sql_password')
                self.sql_password = sql_password.value.decode("utf-8") if sql_password else None
                break
            except:
                time.sleep(random.randint(1, 10))
                i += 1
                if i == self.MAX_TRIES:
                    raise Exception("Too many errors when trying to identify environment variables.")

    def get_env(self):
        """
        returns a dictionary of the environment
        @return:
        """
        return vars(self)

    def sync_with_datastore(self):
        """Takes values stored in runtimeconfig and updates the datastore"""
        self.load_from_runtimeconfig()
        variables = self.get_env()
        if not (admin_info := self.ds.get()):
            admin_info = {'budget_exceeded': False}

        # Load Environment Variables into Datastore
        update = False
        for key, value in variables.items():
            if not any(key == x for x in ['env_dict', 'ds', 'custom_dnszone']):
                if variable := admin_info.get(key, None):
                    if variable == value:
                        # Value is the same ignore
                        continue
                    else:
                        update = True
                else:
                    update = True
                admin_info[key] = value

        if custom_dnszone := variables.get('custom_dnszone', None):
            dnszone = admin_info['dnszone']
            if custom_dnszone != dnszone:
                dnszone = custom_dnszone
                update = True

        if update:
            self.ds.put(admin_info)
            return True
        else:
            return False
