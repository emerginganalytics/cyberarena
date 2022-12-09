from google.cloud import datastore
from datetime import datetime, timedelta, timezone
import yaml
from main_app_utilities.globals import Buckets, PubSub
from main_app_utilities.gcp.cloud_env import CloudEnv
from main_app_utilities.gcp.bucket_manager import BucketManager
from main_app_utilities.infrastructure_as_code.build_spec_to_cloud import BuildSpecToCloud
from cloud_fn_utilities.cyber_arena_objects.unit import Unit


__author__ = "Philip Huff"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Production"


class TestUnit:
    def __init__(self, build_id=None, debug=True):
        self.env = CloudEnv()
        self.bm = BucketManager()
        self.build_id = build_id if build_id else None

    def build(self):
        unit_yaml = self.bm.get(bucket=self.env.spec_bucket, file=f"{Buckets.Folders.SPECS}unit-sample.yaml")
        build_spec = yaml.safe_load(unit_yaml)
        build_spec['workspace_settings'] = {
            'count': 2,
            'registration_required': False,
            'student_emails': [],
            'expires': (datetime.now(timezone.utc).replace(tzinfo=timezone.utc) + timedelta(hours=3)).timestamp()
        }
        build_spec_to_cloud = BuildSpecToCloud(cyber_arena_spec=build_spec, debug=True)
        build_spec_to_cloud.commit()
        build_id = build_spec_to_cloud.get_build_id()
        unit = Unit(build_id=build_id, debug=True, force=True)
        print(f"Beginning to build a new unit with ID {build_id}")
        unit.build()
        print(f"Finished building")
        self.build_id = build_id

    def start(self):
        Unit(build_id=self.build_id, debug=True).start()

    def stop(self):
        Unit(build_id=self.build_id, debug=True).stop()

    def delete(self):
        Unit(build_id=self.build_id, debug=True).delete()


if __name__ == "__main__":
    print(f"Unit v2 Tester.")
    delete_first = str(input(f"Do you want to delete a test unit first? (y/N)"))
    if delete_first and delete_first.upper()[0] == "Y":
        delete_unit = str(input(f"What is the unit ID that you want to delete?"))
        TestUnit(build_id=delete_unit).delete()
        print(f"Unit deletion was successful!")
    build_first = str(input(f"Do you want to build a test unit first? (Y/n)"))
    if not build_first or build_first.upper()[0] == "Y":
        test_unit = TestUnit()
        test_unit.build()
    else:
        test_unit_id = str(input(f"Which unit do you want to test?"))
        test_unit = TestUnit(build_id=test_unit_id)
    while True:
        action = str(input(f"What action are you wanting to test [QUIT], {PubSub.Actions.START.name}, "
                           f"{PubSub.Actions.STOP.name}, or {PubSub.Actions.DELETE.name}?"))
        if not action or action.upper()[0] == "Q":
            break
        if action == PubSub.Actions.START.name:
            test_unit.start()
        elif action == PubSub.Actions.STOP.name:
            test_unit.stop()
        elif action == PubSub.Actions.DELETE.name:
            test_unit.delete()
            break
