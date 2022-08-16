import os
import yaml
import subprocess
from google.cloud import storage
from googleapiclient import discovery
from google.api_core.exceptions import NotFound, Forbidden

from cloud_fn_utilities.gcp.cloud_env import CloudEnv
from install_update.utilities.crypto_lock import CryptoLock
from install_update.utilities.computer_image_sync import ComputerImageSync

__author__ = "Philip Huff"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class BuildSpecification:
    BUILD_SPEC_BUCKET_SUFFIX = "build-specs"
    SPEC_FOLDER = 'specs/'
    STARTUP_SCRIPT_FOLDER = "startup_scripts/"
    TEACHER_FOLDER = "teacher_instructions/"
    STUDENT_FOLDER = "student_instructions/"

    def __init__(self, suppress=True):
        self.suppress = suppress
        self.env = CloudEnv()
        self.build_specs_plaintext = os.path.join("build_files", "specs", "plaintext")
        self.build_specs_encrypted = os.path.join("build_files", "specs", "encrypted")
        self.build_startup_scripts = os.path.join("build_files", "startup_scripts")
        self.build_student_instructions = os.path.join("build_files", "instructions", "student")
        self.build_teacher_instructions_plaintext = os.path.join("build_files", "instructions", "teacher", "plaintext")
        self.build_teacher_instructions_encrypted = os.path.join("build_files", "instructions", "teacher", "encrypted")
        self._create_directories()

        self.storage_client = storage.Client()
        self.service = discovery.build('compute', 'v1')
        try:
            self.build_bucket = self.storage_client.get_bucket(f"{self.env.project}_{self.BUILD_SPEC_BUCKET_SUFFIX}")
        except NotFound as err:
            self.build_bucket = self.storage_client.create_bucket(f"{self.env.project}_{self.BUILD_SPEC_BUCKET_SUFFIX}")
        self.computer_image_sync = ComputerImageSync(suppress=self.suppress)
        self.specs_to_upload = []

    def run(self):
        self._sync_locked_folder(plaintext_dir=self.build_specs_plaintext, encrypted_dir=self.build_specs_encrypted,
                                 extension="yaml")
        upload_specs = self._scan_specs_for_image_sync()
        self._upload_files_to_cloud(upload_specs, self.SPEC_FOLDER)

        self._sync_locked_folder(plaintext_dir=self.build_teacher_instructions_plaintext,
                                 encrypted_dir=self.build_teacher_instructions_encrypted, extension="pdf")
        self._upload_folder_to_cloud(self.build_teacher_instructions_encrypted, self.TEACHER_FOLDER)
        self._upload_folder_to_cloud(self.build_student_instructions, self.STUDENT_FOLDER)
        self._upload_folder_to_cloud(self.build_startup_scripts, self.STARTUP_SCRIPT_FOLDER)


    def _sync_locked_folder(self, plaintext_dir, encrypted_dir, extension):
        spec_crypto_lock = CryptoLock(plaintext_dir=plaintext_dir, encrypted_dir=encrypted_dir,
                                      lock_extension=extension)
        if os.listdir(self.build_specs_plaintext):
            sync_plaintext = True
            if not self.suppress:
                reply = str(input(f"Do you want to first sync all plaintext files in {encrypted_dir}? [Y/n]")).upper()
                sync_plaintext = True if reply == "Y" else False
            if sync_plaintext:
                spec_crypto_lock.encrypt_dir()
        spec_crypto_lock.decrypt_dir()

    def _upload_files_to_cloud(self, files, cloud_directory):
        for file in files:
            self._upload_file_to_cloud(file, cloud_directory)

    def _upload_folder_to_cloud(self, local_directory, cloud_directory, extension=None):
        for item in os.scandir(local_directory):
            if item.is_dir():
                for file in os.scandir(item.path):
                    if not extension or file.suffix == f".{extension}":
                        self._upload_file_to_cloud(file)
            if item.is_file():
                if file.suffix == f".{extension}":
                    self._upload_file_to_cloud(item, cloud_directory)

    def _upload_file_to_cloud(self, file, cloud_directory):
        new_blob = self.build_bucket.blob(f"{cloud_directory}{file.name}")
        with open(file.path, 'rb') as f:
            response = new_blob.upload_from_file(f, content_type='application/octet-stream')

    def _scan_for_computer_images(self):
        for item in os.scandir(self.build_specs_plaintext):
            if item.is_dir():
                child_dir = item.path
                for file in os.scandir(child_dir):
                    if file.suffix == f".yaml":
                        self._sync_computer_images(file.path)
            if item.is_file():
                self._sync_computer_images(item.path)

    def _scan_specs_for_image_sync(self):
        specs_to_upload = []
        for item in os.scandir(self.build_specs_plaintext):
            if item.is_dir():
                for file in os.scandir(item):
                    if self._sync_computer_images(file):
                        specs_to_upload.append(file)
            if item.is_file():
                if self._sync_computer_images(file):
                    specs_to_upload.append(file)
        return specs_to_upload

    def _sync_computer_images(self, file):
        print(f"Beginning to sync images from build specification {file.name}")
        with open(file) as f:
            spec = yaml.safe_load(f)
        server_list = []
        if 'servers' in spec:
            server_list = spec['servers']
        elif 'workspace_servers' in spec:
            server_list = spec['workspace_servers']
        for server_spec in server_list:
            if 'image' in server_spec:
                if not self.computer_image_sync.sync(server_spec['image']):
                    print(f"An error occurred when processing server images for {file.name}. Please correct the "
                          f"error and resync. The specification will not be uploaded to the project until the error "
                          f"is corrected.")
                    return False
                else:
                    return True

    def _create_directories(self):
        directories = [
            self.build_specs_plaintext,
            self.build_specs_encrypted,
            self.build_teacher_instructions_encrypted,
            self.build_startup_scripts,
            self.build_teacher_instructions_plaintext,
            self.build_student_instructions
        ]
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
