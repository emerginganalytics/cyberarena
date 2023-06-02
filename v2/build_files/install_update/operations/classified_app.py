import subprocess
from googleapiclient import discovery

from cloud_fn_utilities.gcp.cloud_env import CloudEnv

__author__ = "Philip Huff"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class ClassifiedApp:
    BUILD_CLOUD_RUN_COMMAND = "gcloud builds submit container-applications/Classified/ " \
                              "--tag gcr.io/{project}/classified"
    DEPLOY_CLOUD_RUN_COMMAND = "gcloud run deploy classified-v2 --image gcr.io/{project}/classified --memory=1024Mi " \
                               "--platform=managed --region={region} --allow-unauthenticated " \
                               "--service-account=cyberarena-service@{project}.iam.gserviceaccount.com"
    MAP_DNS_COMMAND = "gcloud beta run domain-mappings create --service classified-v2 --domain={dns} --region={region}"

    def __init__(self, suppress=True):
        self.suppress = suppress
        self.env = CloudEnv()

    def deploy(self):
        print(f"Beginning to package cloud run app. This operation may take a few minutes...")
        command = self.BUILD_CLOUD_RUN_COMMAND.format(project=self.env.project, region=self.env.region)
        ret = subprocess.run(command, capture_output=True, shell=True)
        print(ret.stderr.decode())
        if ret.returncode != 0:
            print(f"Error packaging the Cloud Run App! See messages above. Existing without deploying the "
                  f"Cloud Run App")
            return False
        command = self.DEPLOY_CLOUD_RUN_COMMAND.format(project=self.env.project, region=self.env.region)
        ret = subprocess.run(command, capture_output=True, shell=True)
        print(ret.stderr.decode())
        if ret.returncode != 0:
            print(f"Error packaging the Cloud Run App! See messages above. Existing without deploying the "
                  f"Cloud Run App")
            return False

        # Not sure what values I can place here
        """
        confirmation = str(input(f"Do you want to map the main app to the DNS record "
                                 f"{self.env.main_app_url}? (y/N): ")).upper() \
            if not self.suppress else "N"
        if confirmation == "N":
            command = self.MAP_DNS_COMMAND.format(dns=self.env.main_app_url, region=self.env.region)
            ret = subprocess.run(command, capture_output=True, shell=True)
            print(ret.stderr.decode())
        """
        return True
