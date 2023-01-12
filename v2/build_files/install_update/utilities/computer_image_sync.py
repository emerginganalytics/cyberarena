from datetime import datetime
import subprocess
from googleapiclient import discovery
from googleapiclient.errors import HttpError

from cloud_fn_utilities.gcp.cloud_env import CloudEnv
from cloud_fn_utilities.gcp.cloud_operations_manager import CloudOperationsManager

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
        self.cloud_ops_mgr = CloudOperationsManager()
        self.source_image_project = self.SOURCE_IMAGE_PROJECT
        reply = str(input(f"The source project for sync'ing compute images is {self.source_image_project}. Do you "
                          f"wish to continue with this project? [Y/n]")).upper()
        if reply == "N":
            reply = str(input(f"Enter the project ID of the source project for sync'ing compute images"))
            self.source_image_project = reply

    def sync(self, image_name, source_project=None):
        source_project = source_project if source_project else self.source_image_project
        try:
            src_image = self.service.images().get(project=source_project, image=image_name).execute()
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

    def image_server(self, image_server_name: str):
        """
        Create a new image of the server in the cloud project. Remove the 'image_' prefix for the server to infer
        the cloud server name.
        Args:
            image_server_name (str): The name of the image needed.

        Returns: None

        """
        server_name = image_server_name.replace("image-", "")
        self._create_production_image(server_name=server_name)

    def _copy_image(self, image_name, delete_previous=False):
        print(f"\t...Beginning to copy {image_name} from {self.source_image_project} to {self.env.project}...")
        if delete_previous:
            command = self.DELETE_IMAGE_COMMAND.format(project=self.env.project, image=image_name)
            ret = subprocess.run(command, capture_output=True, shell=True)
            print(ret.stderr.decode())
            if ret.returncode != 0:
                print(f"\t...Error deleting image {image_name} in project {self.env.project}")
                return False
        command = self.COPY_IMAGE_COMMAND.format(src_project=self.source_image_project, dst_project=self.env.project,
                                                 image=image_name)
        ret = subprocess.run(command, capture_output=True, shell=True)
        print(ret.stderr.decode())
        if ret.returncode != 0:
            print(f"\t...Error copying the server image {image_name} to project {self.env.project}")
            return False

    def _create_production_image(self, server_name, base_image_name=None, existing_snapshot=None, max_snapshots=3):
        """
        Create a new production image.
        :param image_version: The version of the image as determined by the application
        :param server_name: Used for testing to provide an existing snapshot to image
        :param image_name: Specify the image name if different than the one derived by the server_name
        :param existing_snapshot: Provided for testing purposes if a snapshot already exists
        :returns: None
        """
        # First try and create a new snapshot image.
        if existing_snapshot:
            snapshot_name = existing_snapshot
        else:
            snapshot_name = self._create_snapshot_from_disk(server_name, base_image_name, max_snapshots)

        if snapshot_name:
            image_name = server_name if not base_image_name else base_image_name
            prod_image = f'image-{image_name}'
            i = 0
            delete_success = False
            nothing_to_delete = False
            while not delete_success and i < 5 and not nothing_to_delete:
                try:
                    response = self.service.images().delete(project=self.env.project, image=prod_image).execute()
                    delete_success = True
                    print(f'\t...Sent job to delete the production image before creating a new one, '
                          f'and waiting for response')
                except HttpError:
                    nothing_to_delete = True
                except BrokenPipeError:
                    i += 1
            if not delete_success and not nothing_to_delete:
                raise Exception(f"Error deleting image {prod_image}")

            if not nothing_to_delete:
                if not self.cloud_ops_mgr.wait_for_completion(operation_id=response['id'],
                                                              wait_type=CloudOperationsManager.WaitTypes.GLOBAL):
                    raise Exception(f"Timeout waiting for image {prod_image} to delete.")

            # If the image was successfully deleted, then build the new image.
            image_body = {
                'name': prod_image,
                'description': 'Cyber Arena production image',
                'sourceSnapshot': f'projects/{self.env.project}/global/snapshots/{snapshot_name}'
            }
            i = 0
            build_success = False
            while not build_success and i < 5:
                try:
                    response = self.service.images().insert(project=self.env.project, body=image_body).execute()
                    build_success = True
                    print(f'\t...Sent job to create the new production image, and waiting for response')
                except BrokenPipeError:
                    i += 1
                if build_success and \
                    not self.cloud_ops_mgr.wait_for_completion(operation_id=response['id'],
                                                               wait_type=CloudOperationsManager.WaitTypes.GLOBAL):
                    raise Exception(f"Timeout waiting to insert {prod_image}")
            return True
        else:
            return False

    def _create_snapshot_from_disk(self, disk, base_image_name=None, max_snapshots=3):
        """
        This function keeps at most 2 snapshot available from a server
        param disk: The name of the server
        return: Either the name of the new snapshot or None
        """
        found_available = False
        latest = 0
        latest_ts = '2000-01-01T00:00:00.000'
        i = 0

        if base_image_name:
            base_snapshot_name = base_image_name
        else:
            base_snapshot_name = disk

        while i < max_snapshots:
            try:
                response = self.service.snapshots().get(project=self.env.project,
                                                        snapshot=base_snapshot_name + str(i)).execute()
                if response['creationTimestamp'] > latest_ts:
                    latest_ts = response['creationTimestamp']
                    latest = i
                i += 1
            except HttpError:
                latest = (i - 1) % max_snapshots
                found_available = True
                break

        selected_snapshot = f"{base_snapshot_name}{(latest + 1) % max_snapshots}"
        if not found_available:
            response = self.service.snapshots().delete(project=self.env.project, snapshot=selected_snapshot).execute()

            if not self.cloud_ops_mgr.wait_for_completion(operation_id=response['id'],
                                                          wait_type=CloudOperationsManager.WaitTypes.GLOBAL):
                raise Exception(f"Timeout waiting for snapshot {selected_snapshot} to delete.")

        snapshot_body = {
            'name': selected_snapshot,
            'description': 'Production snapshot used for imaging'
        }

        response = self.service.disks().createSnapshot(project=self.env.project, zone=self.env.zone, disk=disk,
                                                       body=snapshot_body).execute()

        if not self.cloud_ops_mgr.wait_for_completion(operation_id=response['id'],
                                                      wait_type=CloudOperationsManager.WaitTypes.ZONE):
            raise Exception(f"Timeout waiting for snapshot {selected_snapshot} to be created")

        return selected_snapshot
