from google.cloud import runtimeconfig
import os

__author__ = "Ryan Ronquillo"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Ryan Ronquillo"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Ryan Ronquillo"
__email__ = "rfronquillo@ualr.edu"
__status__ = "Testing"

class CloudEnv:
    def __init__(self):
        creds = ''
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = creds
        runtimeconfig_client = runtimeconfig.Client()
        myconfig = runtimeconfig_client.config('cybergym')
        self.project = myconfig.get_variable('project').value.decode('utf-8')
        self.region = myconfig.get_variable('region').value.decode('utf-8')
        self.zone = myconfig.get_variable('zone').value.decode('utf-8')
        self.zone = myconfig.get_variable('dns_suffix').value.decode('utf-8')
        self.topic = os.environ.get('test')
        self.build_id = os.environ.get('')
        self.build_type = os.environ.get('')
        self.telemetry_url = os.environ.get('')
