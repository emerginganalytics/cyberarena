import yaml
import subprocess
from googleapiclient import discovery
from googleapiclient.errors import HttpError

from cloud_fn_utilities.gcp.cloud_env import CloudEnv


class ComputerImageSync:
    GLOBAL_IMAGE_REPO = "ualr-cybersecurity"
    COPY_IMAGE_COMMAND = "gcloud compute --project={project} images create {image} --source-image={image} " \
                         "--source-image-project=ualr-cybersecurity"

    def __init__(self, suppress=True):
        self.suppress = suppress
        self.env = CloudEnv()
        self.service = discovery.build('compute', 'v1')

    def sync(self, image_name):
        try:
            response = self.service.images().get(project=self.env.project, image=image_name).execute()

        except HttpError as err:
            if err.resp.status == 404:
                # TODO: Handle the case where the server image does not exist
                pass
        command = self.COPY_IMAGE_COMMAND.format(project=self.env.project, image=image_name)
        ret = subprocess.run(command, capture_output=True, shell=True)
        print(ret.stderr.decode())
        if ret.returncode != 0:
            print(f"Error copying the server image {image_name} to project {self.envproject}"
                  f"Cloud Run App")
            return False
