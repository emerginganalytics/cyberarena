from datetime import datetime
import subprocess
from googleapiclient import discovery
from googleapiclient.errors import HttpError

from cloud_fn_utilities.gcp.cloud_env import CloudEnv

__author__ = "Philip Huff"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class ComputerImageSync:
    SOURCE_IMAGE_PROJECT = "ualr-cybersecurity"
    DELETE_IMAGE_COMMAND = "gcloud compute --project={project} images delete {image} --quiet"
    COPY_IMAGE_COMMAND = "gcloud compute --project={dst_project} images create {image} --source-image={image} " \
                         "--source-image-project={src_project}"

    def __init__(self, suppress=True):
        self.suppress = suppress
        self.env = CloudEnv()
        self.service = discovery.build('compute', 'v1')
        self.source_image_project = self.SOURCE_IMAGE_PROJECT
        reply = str(input(f"The source project for sync'ing compute images is {self.source_image_project}. Do you "
                          f"wish to continue with this project? [Y/n]")).upper()
        if reply == "N":
            reply = str(input(f"Enter the project ID of the source project for sync'ing compute images"))
            self.source_image_project = reply

    def sync(self, image_name):
        try:
            src_image = self.service.images().get(project=self.source_image_project, image=image_name).execute()
            src_creation_ts = datetime.fromisoformat(src_image['creationTimestamp'])
        except HttpError as err:
            print(f"ERROR: The source image {image_name} does not exist or cannot connect to project. Make sure the "
                  f"project service account has Compute Image User access to the project {self.source_image_project}"
                  f"\n{err.error_details}")
            return False

        try:
            dst_image = self.service.images().get(project=self.env.project, image=image_name).execute()
            dst_creation_ts = datetime.fromisoformat(dst_image['creationTimestamp'])
            if src_creation_ts > dst_creation_ts:
                return self._copy_image(image_name, delete_previous=True)
        except HttpError as err:
            # If a 404 error, then the image does not exist and needs to be copied over.
            if err.resp.status == 404:
                return self._copy_image(image_name)
        return True

    def _copy_image(self, image_name, delete_previous=False):
        print(f"Beginning to copy {image_name} from {self.source_image_project} to {self.env.project}...")
        if delete_previous:
            command = self.DELETE_IMAGE_COMMAND.format(project=self.env.project, image=image_name)
            ret = subprocess.run(command, capture_output=True, shell=True)
            print(ret.stderr.decode())
            if ret.returncode != 0:
                print(f"Error deleting image {image_name} in project {self.env.project}")
                return False
        command = self.COPY_IMAGE_COMMAND.format(src_project=self.source_image_project, dst_project=self.env.project,
                                                 image=image_name)
        ret = subprocess.run(command, capture_output=True, shell=True)
        print(ret.stderr.decode())
        if ret.returncode != 0:
            print(f"Error copying the server image {image_name} to project {self.env.project}")
            return False
