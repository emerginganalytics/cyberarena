# TODO: These classes are unfinished. The goal is to upload all of the specification data similar to v1,
# TODO: But in v2, we also want to synchronize computer images based on the specifications to ensure a project
# TODO: will have the correct images.

import os
import yaml
import subprocess
from google.cloud import storage
from googleapiclient import discovery
from google.api_core.exceptions import NotFound

from cloud_fn_utilities.gcp.cloud_env import CloudEnv
from install_update.utilities.crypto_lock import CryptoLock
from install_update.utilities.computer_image_sync import ComputerImageSync


class BuildSpecification:
    BUILD_SPEC_BUCKET = "cyber_arena_build_specs"
    SPEC_FOLDER = 'specs/'
    STARTUP_SCRIPT_FOLDER = "startup_scripts/"
    TEACHER_FOLDER = "teacher_instructions/"
    STUDENT_FOLDER = "student_instructions/"

    def __init__(self, suppress=True):
        self.suppress = suppress
        self.env = CloudEnv()
        self.build_specs_plaintext = os.path.join("..", "specs", "plaintext")
        self.build_specs_encrypted = os.path.join("..", "specs", "encrypted")
        self.build_startup_scripts = os.path.join("..", "startup_scripts")
        self.build_student_instructions = os.path.join("..", "instructions", "student")
        self.build_teacher_instructions_plaintext = os.path.join("..", "instructions", "teacher", "plaintext")
        self.build_teacher_instructions_encrypted = os.path.join("..", "instructions", "teacher", "encrypted")
        self.storage_client = storage.Client()
        self.service = discovery.build('compute', 'v1')
        try:
            self.build_bucket = self.storage_client.get_bucket(self.BUILD_SPEC_BUCKET)
        except NotFound:
            self.build_bucket = self.storage_client.create_bucket(self.BUILD_SPEC_BUCKET)
        self.computer_image_sync = ComputerImageSync(suppress=self.suppress)

    def run(self):
        self._process_locked_folder(plaintext_dir=self.build_specs_plaintext, encrypted_dir=self.build_specs_encrypted,
                                    cloud_dir=self.SPEC_FOLDER, extension="yaml")
        self._process_locked_folder(plaintext_dir=self.build_teacher_instructions_plaintext,
                                    encrypted_dir=self.build_teacher_instructions_encrypted, extension="pdf")
        self._upload_folder_to_cloud(self.build_student_instructions, self.STUDENT_FOLDER)
        self._upload_folder_to_cloud(self.build_startup_scripts, self.STARTUP_SCRIPT_FOLDER)


    def _process_locked_folder(self, plaintext_dir, encrypted_dir, cloud_dir, extension):
        spec_crypto_lock = CryptoLock(plaintext_dir=plaintext_dir, encrypted_dir=encrypted_dir,
                                      lock_extension=extension)
        if not os.listdir(self.build_specs_plaintext):
            sync_plaintext = True
            if not self.suppress:
                reply = str(input(f"Do you want to first sync all plaintext files in {encrypted_dir}? [Y/n]")).upper()
                sync_plaintext = True if reply == "Y" else False
            if sync_plaintext:
                spec_crypto_lock.encrypt_dir()

        spec_crypto_lock.decrypt_dir()
        self._sync_computer_images()
        self._upload_file_to_cloud(plaintext_dir, cloud_dir, extension)

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
            new_blob.upload_from_file(f, content_type='application/octet-stream')

    def _scan_for_computer_images(self):
        for item in os.scandir(self.build_specs_plaintext):
            if item.is_dir():
                child_dir = item.path
                for file in os.scandir(child_dir):
                    if file.suffix == f".yaml":
                        self._sync_computer_images(file.path)
            if item.is_file():
                self._sync_computer_images(item.path)

    def _sync_computer_images(self, file):
        with open(file) as f:
            spec = yaml.safe_load(f)
        if 'servers' in spec:
            for server_spec in spec['servers']:
                if 'image' in server_spec:
                    if not self.computer_image_sync.sync(server_spec['image']):
                        # TODO: Ask the user if they want to rectify the problem or skip uploading the yaml file.
                        pass