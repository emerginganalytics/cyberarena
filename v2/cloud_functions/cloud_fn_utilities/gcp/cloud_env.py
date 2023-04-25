import random
import time
from google.cloud import runtimeconfig
from googleapiclient.errors import HttpError

__author__ = "Philip Huff"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff"]
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
        self.env_dict = env_dict
        if self.env_dict:
            if not type(self.env_dict) == dict:
                raise TypeError(f'Improper type {type(self.env_dict)} for cls arg')
            self.project = self.env_dict['project']
            self.project_number = self.env_dict.get('project_number', None)
            self.region = self.env_dict['region']
            self.zone = self.env_dict['zone']
            self.dns_suffix = self.env_dict['dns_suffix']
            self.api_key = self.env_dict['api_key']
            self.custom_dnszone = self.env_dict['custom_dnszone']
            self.dnszone = self.env_dict['dnszone']
            self.student_instructions_url = self.env_dict['student_instructions_url']
            self.teacher_instructions_url = self.env_dict['teacher_instructions_url']
            self.main_app_url = self.env_dict['main_app_url']
            self.main_app_v2_url = self.env_dict['main_app_v2_url']
            self.guac_db_password = self.env_dict['guac_db_password']
            self.max_workspaces = self.env_dict['max_workspaces']
            self.sql_ip = self.env_dict.get('sql_ip', None)
            self.sql_password = self.env_dict.get('sql_password', None)
            self.timezone = self.env_dict.get('timezone', 'America/Chicago')
        else:
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
                    self.student_instructions_url = student_instructions_url.value.decode("utf-8") if student_instructions_url else \
                        'https://storage.googleapis.com/student_workout_instructions_ualr-cybersecurity/'
                    teacher_instructions_url = myconfig.get_variable('teacher_instructions_url')
                    self.teacher_instructions_url = teacher_instructions_url.value.decode("utf-8") if teacher_instructions_url else \
                        'https://storage.googleapis.com/teacher_workout_instructions_ualr-cybersecurity/'
                    self.main_app_url = myconfig.get_variable('main_app_url').value.decode("utf-8")
                    main_app_v2_url = myconfig.get_variable('main_app_v2_url')
                    if main_app_v2_url:
                        self.main_app_v2_url = main_app_v2_url.value.decode("utf-8")
                    else:
                        self.main_app_v2_url = self.main_app_url
                    self.guac_db_password = myconfig.get_variable('guac_password').value.decode("utf-8")
                    max_workspaces = myconfig.get_variable('max_workspaces')
                    self.max_workspaces = int(max_workspaces.value.decode("utf-8")) if max_workspaces else 100
                    sql_ip = myconfig.get_variable('sql_ip')
                    self.sql_ip = sql_ip.value.decode("utf-8") if sql_ip else None
                    sql_password = myconfig.get_variable('sql_password')
                    self.sql_password = sql_password.value.decode("utf-8") if sql_password else None
                    timezone = myconfig.get_variable('timezone', None)
                    if timezone:
                        self.timezone = timezone.value.decode('utf-8')
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
