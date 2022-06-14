from google.cloud import runtimeconfig

__author__ = "Philip Huff"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class CloudEnv:
    def __init__(self):
        runtimeconfig_client = runtimeconfig.Client()
        myconfig = runtimeconfig_client.config('cybergym')
        self.project = myconfig.get_variable('project').value.decode("utf-8")
        self.region = myconfig.get_variable('region').value.decode("utf-8")
        self.zone = myconfig.get_variable('zone').value.decode("utf-8")
        self.dns_suffix = myconfig.get_variable('dns_suffix').value.decode("utf-8")
        self.script_repository = myconfig.get_variable('script_repository').value.decode("utf-8")
        self.api_key = myconfig.get_variable('api_key').value.decode("utf-8")
        self.custom_dnszone = myconfig.get_variable('dnszone')
        student_instructions_url = myconfig.get_variable('student_instructions_url')
        self.student_instructions_url = student_instructions_url.value.decode("utf-8") if student_instructions_url else \
            'https://storage.googleapis.com/student_workout_instructions_ualr-cybersecurity/'
        teacher_instructions_url = myconfig.get_variable('teacher_instructions_url')
        self.teacher_instructions_url = teacher_instructions_url.value.decode("utf-8") if teacher_instructions_url else \
            'https://storage.googleapis.com/teacher_workout_instructions_ualr-cybersecurity/'
        if self.custom_dnszone != None:
            self.dnszone = self.custom_dnszone.value.decode("utf-8")
        else:
            self.dnszone = 'cybergym-public'
        self.main_app_url = myconfig.get_variable('main_app_url').value.decode("utf-8")
        self.guac_db_password = myconfig.get_variable('guac_password').value.decode("utf-8")
        max_workspaces = myconfig.get_variable('max_workspaces')
        self.max_workspaces = int(max_workspaces.value.decode("utf-8")) if max_workspaces else 100
