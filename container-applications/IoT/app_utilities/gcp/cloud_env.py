from google.cloud import runtimeconfig
import time
import random
from app_utilities.gcp.datastore_manager import DataStoreManager
from app_utilities.globals import DatastoreKeyTypes

__author__ = "Philip Huff"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff", "Andrew Bomberger", "Ryan Ebsen"]
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
            # Project Variables
            self.project = self.env_dict['project']
            self.region = self.env_dict['region']
            self.zone = self.env_dict['zone']
            self.dns_suffix = self.env_dict['dns_suffix']
            self.dnszone = self.env_dict['dnszone']
            self.timezone = self.env_dict.get('timezone', 'America/Chicago')
            # Cyber Arena Variables
            self.admin_email = self.env_dict['admin_email']
            self.main_app_url = self.env_dict['main_app_url']
            self.main_app_v2_url = self.env_dict['main_app_url_v2']
            # API Keys
            self.api_key = self.env_dict['api_key']
            self.shodan_api_key = self.env_dict.get('shodan_api_key', None)
        else:
            runtimeconfig_client = runtimeconfig.Client()
            myconfig = runtimeconfig_client.config('cybergym')
            i = 0
            while i < self.MAX_TRIES:
                try:
                    self.project = myconfig.get_variable('project').value.decode("utf-8")
                    self.region = myconfig.get_variable('region').value.decode("utf-8")
                    self.zone = myconfig.get_variable('zone').value.decode("utf-8")
                    self.dns_suffix = myconfig.get_variable('dns_suffix').value.decode("utf-8")
                    self.api_key = myconfig.get_variable('api_key').value.decode("utf-8")
                    timezone = myconfig.get_variable('timezone', None)
                    if timezone:
                        self.timezone = timezone.value.decode('utf-8')
                    else:
                        self.timezone = 'America/Chicago'
                    self.custom_dnszone = myconfig.get_variable('dnszone')
                    if self.custom_dnszone is not None:
                        self.dnszone = self.custom_dnszone.value.decode("utf-8")
                    else:
                        self.dnszone = 'cybergym-public'
                    self.main_app_url = myconfig.get_variable('main_app_url').value.decode("utf-8")
                    main_app_url_v2 = myconfig.get_variable('main_app_url_v2')
                    if main_app_url_v2:
                        self.main_app_url_v2 = main_app_url_v2.value.decode("utf-8")
                    else:
                        self.main_app_url_v2 = self.main_app_url
                    self.admin_email = myconfig.get_variable('admin_email').value.decode("utf-8")
                    shodan_api_key = myconfig.get('shodan_api_key', None)
                    if shodan_api_key:
                        self.shodan_api_key = shodan_api_key.value.decode('utf-8')
                    self.auth_config = {
                        'api_key': self.api_key,
                        'auth_domain': str(self.project + ".firebaseapp.com"),
                        'project_id': self.project
                    }
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
