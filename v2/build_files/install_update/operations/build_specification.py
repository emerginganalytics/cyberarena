"""
Manage the build specification synchronization with the cloud.

This module contains the following classes:
    - BuildSpecification: Operations to sync local specifications with the cloud project.
"""
import datetime
import os
import random
import string
import subprocess
import yaml
from google.cloud import storage
from googleapiclient import discovery
from google.api_core.exceptions import NotFound, Forbidden
from marshmallow import ValidationError


from main_app_utilities.globals import BuildConstants
from main_app_utilities.infrastructure_as_code.schema import FixedArenaSchema, FixedArenaClassSchema, UnitSchema
from main_app_utilities.infrastructure_as_code.object_validators.unit_object_validator import UnitValidator
from cloud_fn_utilities.gcp.cloud_env import CloudEnv
from cloud_fn_utilities.gcp.datastore_manager import DataStoreManager, DatastoreKeyTypes
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
    ATTACK_FOLDER = 'attacks/'
    STARTUP_SCRIPT_FOLDER = "startup_scripts/"
    TEACHER_FOLDER = "teacher_instructions/"
    STUDENT_FOLDER = "student_instructions/"

    def __init__(self, sync=True, suppress=True):
        self.suppress = suppress
        self.env = CloudEnv()
        self.build_attacks_specs = os.path.join("build_files", "specs", "attacks")
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
        if sync:
            self.computer_image_sync = ComputerImageSync(suppress=self.suppress)
        self.specs_to_upload = []

    def run(self):
        self._sync_locked_folder(plaintext_dir=self.build_specs_plaintext, encrypted_dir=self.build_specs_encrypted,
                                 extension="yaml")
        upload_specs = self._scan_specs_for_image_sync()
        self._upload_files_to_cloud(upload_specs, self.SPEC_FOLDER)
        self._sync_specs_to_datastore(upload_specs)

        self._sync_locked_folder(plaintext_dir=self.build_teacher_instructions_plaintext,
                                 encrypted_dir=self.build_teacher_instructions_encrypted, extension="pdf")
        self._upload_folder_to_cloud(self.build_teacher_instructions_encrypted, self.TEACHER_FOLDER)
        self._upload_folder_to_cloud(self.build_student_instructions, self.STUDENT_FOLDER)
        self._upload_folder_to_cloud(self.build_startup_scripts, self.STARTUP_SCRIPT_FOLDER)
        self._upload_folder_to_cloud(self.build_attacks_specs, self.ATTACK_FOLDER)
        self._sync_attacks_to_cloud()

    def sync_single_spec(self):
        """
        Sync's a single specification file. This can be used by instructors after creating everything needed for the
        specification file. This functions will open the file and serialize the contents to ensure it is a valid
        specification. Then, it scans through the images. If the image does not exist, it will create new images based
        on the server name or return an error.
        Args:
            None

        Returns: None

        """
        spec_file = str(input(f"What is the directory and filename path to the spec file "
                              f"(do not include the specs/plaintext path)? "))
        filename = f"build_files/specs/plaintext/{spec_file}"
        with open(filename) as f:
            spec = yaml.safe_load(f)
        # If the spec is not a valid schema. This next function will throw an error.
        try:
            self._validate_spec(spec)
        except ValidationError as e:
            print(f"\t...Validation Error in the file: {e.messages}")
            return
        print(f"\t...Specification passed validation testing.")
        response = str(input(f"Do you have servers ready to image in this project for the specification? "
                             f"If 'N', the source project will be used to sync images (y/N)"))
        image_first = True if str.upper(response) == "Y" else False
        source_project = None
        if not image_first:
            source_project = str(input(f"Enter the source project name you would like to use for copying over images "
                                       f"(or press enter if you want to use the default project)"))
        self._sync_computer_images(file=filename, image_first=image_first, source_project=source_project)
        print(f"\t...Completed processing computing images.")
        print(f"\t...Uploading the specification to the cloud.")
        self._upload_file_to_cloud(file=filename, cloud_directory=self.SPEC_FOLDER)
        print(f"\t...The specification {spec_file} has been successfully uploaded to the cloud project "
              f"{self.env.project}.")
        print(f"\t...Encrypting the spec to ensure the encrypted spec is available in the repo.")
        self._sync_locked_folder(plaintext_dir=self.build_specs_plaintext, encrypted_dir=self.build_specs_encrypted,
                                 extension="yaml")
        print(f"\t...Encryption is complete.")

    def decrypt_locked_folders(self):
        print(f'\t...Beginning decryption process')
        spec_crypto_lock = CryptoLock(plaintext_dir=self.build_specs_plaintext,
                                      encrypted_dir=self.build_specs_encrypted, lock_extension='yaml')
        spec_crypto_lock.decrypt_dir()
        print(f'\t...Decryption complete.')

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
                        self._upload_file_to_cloud(file, cloud_directory)
            if item.is_file():
                if not extension or item.suffix == f".{extension}":
                    self._upload_file_to_cloud(item, cloud_directory)

    def _upload_file_to_cloud(self, file, cloud_directory):
        if type(file) == str:
            file_name = file.split('/')[-1]
        else:
            file_name = file.name
        new_blob = self.build_bucket.blob(f"{cloud_directory}{file_name}")
        with open(file, 'rb') as f:
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
                    self._sync_computer_images(file)
                    specs_to_upload.append(file)
            if item.is_file():
                self._sync_computer_images(item)
                specs_to_upload.append(item)
        return specs_to_upload

    def _sync_computer_images(self, file, image_first=False, source_project=None):
        print(f"\t...Beginning to sync images from build specification {file}")
        with open(file) as f:
            spec = yaml.safe_load(f)
        server_list = []
        if 'servers' in spec:
            server_list = spec['servers']
        elif 'workspace_servers' in spec:
            server_list = spec['workspace_servers']
        for server_spec in server_list:
            if 'image' in server_spec:
                if image_first:
                    print(f"\t...Beginning to IMAGE the server image {server_spec['image']}")
                    self.computer_image_sync.image_server(server_spec['image'])
                else:
                    print(f"\t...Beginning to SYNC the server image {server_spec['image']}")
                    self.computer_image_sync.sync(server_spec['image'], source_project)
                print(f"\t...Finished processing {server_spec['image']}")

    def _sync_attacks_to_cloud(self):
        ds_manager = DataStoreManager()

        # First update files stored in Cloud buckets
        self._upload_folder_to_cloud(self.build_attacks_specs, self.ATTACK_FOLDER)
        # Load file into python objects and update each datastore entry
        for filename in os.listdir(self.build_attacks_specs):
            attack = yaml.safe_load(open(os.path.join(self.build_attacks_specs, filename)))
            ds_manager.set(key_type=DatastoreKeyTypes.CYBERARENA_ATTACK_SPEC.value, key_id=attack['id'])
            ds_manager.put(attack)

    def _sync_specs_to_datastore(self, specs):
        ds_manager = DataStoreManager()

        # Load each spec in plaintext dir and generate the datastore entry to upload
        for filename in specs:
            print(f"\t...Beginning to SYNC the specification {filename.name} to Datastore")
            spec = yaml.safe_load(open(filename.path))
            self._validate_spec(spec)
            spec['id'] = ''.join(random.choice(string.ascii_lowercase) for j in range(10))
            ds_manager.set(key_type=DatastoreKeyTypes.CATALOG.value, key_id=spec['id'])
            ds_manager.put(spec)

    def _create_directories(self):
        directories = [
            self.build_attacks_specs,
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

    @staticmethod
    def _validate_spec(spec):
        if 'build_type' not in spec:
            raise ValidationError("Spec does not contain a build_type")
        # Add the dynamic fields required for a spec to avoid throwing errors on these
        spec['creation_timestamp'] = datetime.datetime.now().timestamp()
        build_type = spec['build_type']
        if build_type == BuildConstants.BuildType.FIXED_ARENA.value:
            spec = FixedArenaSchema().load(spec)
        elif build_type == BuildConstants.BuildType.FIXED_ARENA_CLASS.value:
            spec['fixed_arena_servers'] = []
            spec = FixedArenaClassSchema().load(spec)
        elif build_type in [BuildConstants.BuildType.UNIT.value, BuildConstants.BuildType.ESCAPE_ROOM.value]:
            spec['instructor_id'] = 'instructor@example.com'
            spec = UnitSchema().load(spec)
            spec = UnitValidator().load(spec)
        return spec
