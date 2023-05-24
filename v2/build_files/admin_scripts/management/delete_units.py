from google.cloud import datastore
from datetime import datetime, timedelta, timezone
import yaml
from main_app_utilities.globals import Buckets, PubSub, DatastoreKeyTypes
from main_app_utilities.gcp.cloud_env import CloudEnv
from main_app_utilities.gcp.datastore_manager import DataStoreManager
from main_app_utilities.infrastructure_as_code.build_spec_to_cloud import BuildSpecToCloud
from cloud_fn_utilities.cyber_arena_objects.unit import Unit
from cloud_fn_utilities.periodic_maintenance.hourly_maintenance import HourlyMaintenance


__author__ = "Philip Huff"
__copyright__ = "Copyright 2023, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Production"


class DeleteTestManager:
    def __init__(self, debug=False):
        self.env = CloudEnv()
        self.ds = DataStoreManager(key_type=DatastoreKeyTypes.WORKOUT)

    def run(self):
        delete_tests = str(input(f"Do you want to delete all tests for the project {self.env.project}? (Y/n) "))
        if not delete_tests or delete_tests.upper()[0] == "Y":
            for build_id in self.ds.query(filters=[('test', '=', True)]):
                self.delete(build_id=build_id)
        delete_expired = str(input(f"Do you want to run the deletion routine for expired units for the "
                                   f"project {self.env.project}? (Y/n) "))
        if not delete_expired or delete_expired.upper()[0] == "Y":
            HourlyMaintenance().run()

    def delete(self, build_id):
        Unit(build_id=build_id).delete()


if __name__ == "__main__":
    print(f"An automated script to delete entire units.")
    DeleteTestManager().run()
