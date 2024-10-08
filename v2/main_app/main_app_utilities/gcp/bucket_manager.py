import logging
from google.cloud import logging_v2
from google.cloud import storage
from main_app_utilities.gcp.cloud_env import CloudEnv
from main_app_utilities.globals import Buckets

__author__ = "Philip Huff"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff", "Andrew Bomberger"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class BucketManager:
    BUILD_SPEC_BUCKET_SUFFIX = "build-specs"
    SPEC_FOLDER = 'specs/'
    ATTACK_FOLDER = 'attacks/'
    STARTUP_SCRIPT_FOLDER = "startup_scripts/"
    TEACHER_FOLDER = "teacher_instructions/"
    STUDENT_FOLDER = "student_instructions/"

    def __init__(self, env_dict=None):
        self.env = CloudEnv(env_dict=env_dict) if env_dict else CloudEnv()
        log_client = logging_v2.Client()
        log_client.setup_logging()
        self.bucket_manager = storage.Client()

    def get(self, bucket, file):
        bucket = self.bucket_manager.get_bucket(bucket)
        blob = bucket.get_blob(file)
        if not blob:
            logging.error(f"The file {file} in bucket {bucket} was not found.")
            raise FileNotFoundError
        file_contents = blob.download_as_string()
        return file_contents

    def put(self, bucket, file):
        new_bucket = self.bucket_manager.get_bucket(bucket)
        filename = f'{bucket}{file}'.lower()
        new_blob = new_bucket.blob(filename)
        with open(filename, 'rb') as temp:
            new_blob.upload_from_file(temp, content_type='application/octet-stream')
            temp.close()

    def get_scripts(self):
        """
        Get the names of scripts in the spec folder.
        Returns: List

        """
        bucket = self.bucket_manager.get_bucket(f"{self.env.project}_{self.BUILD_SPEC_BUCKET_SUFFIX}")
        scripts = []
        for blob in bucket.list_blobs(prefix=self.STARTUP_SCRIPT_FOLDER):
            scripts.append(blob.name)
        return scripts

    def get_workouts(self):
        """Retrieves list of standard Cyber Gym workout spec files"""
        folder_name = Buckets.Folders.SPECS.value
        bucket = self.bucket_manager.get_bucket(CloudEnv().spec_bucket)

        workout_specs = []
        for blob in bucket.list_blobs(prefix=folder_name):
            blob_name = blob.name
            formatted_blob_name = blob_name.replace(folder_name, "").split('.')[0]
            if formatted_blob_name != "":
                workout_specs.append(formatted_blob_name)
        return workout_specs

    def get_attacks(self):
        # TODO: Update the following two lines to match current standards
        bucket_name = 'ualr-cybersecurity_build-specs'
        folder_name = 'attacks'
        bucket = self.bucket_manager.get_bucket(bucket_name)

        attacks = []
        for blob in bucket.list_blobs(prefix=folder_name):
            blob_name = blob.name
            formatted_blob_name = blob_name.replace(folder_name, "").split('/')[1]
            if formatted_blob_name != 'attack.yaml':
                attack_spec = blob.download_as_string()
                attacks.append(attack_spec)
        return attacks

    def get_class_list(self):
        """Returns list of all spec names used for building fixed-arena classes"""
        bucket = self.bucket_manager.get_bucket(self.env.spec_bucket)
        class_list = []
        for blob in bucket.list_blobs():
            formatted_blob_name = blob.name.replace(self.env.spec_bucket, "").split('/')[1]
            if 'class' in formatted_blob_name:
                class_list.append(formatted_blob_name.split(".yaml")[0])
        return class_list

    def get_fixed_arena_list(self):
        """Returns list of all spec names used for fixed-arena builds"""
        bucket = self.bucket_manager.get_bucket(self.env.spec_bucket)
        fa_list = []
        for blob in bucket.list_blobs():
            formatted_blob_name = blob.name.replace(self.env.spec_bucket, "").split('/')[1]
            if 'class' not in formatted_blob_name and 'workout' not in formatted_blob_name:
                fa_list.append(formatted_blob_name.split(".yaml")[0])
        return fa_list
