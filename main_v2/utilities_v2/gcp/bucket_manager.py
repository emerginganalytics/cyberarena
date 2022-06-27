import logging
from google.cloud import logging_v2
from google.cloud import storage

from utilities_v2.gcp.cloud_env import CloudEnv

__author__ = "Philip Huff"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class BucketManager:
    def __init__(self):
        self.env = CloudEnv()
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
