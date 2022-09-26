from v2.cloud_functions.cloud_fn_utilities.periodic_maintenance.daily_maintenance import DailyMaintenance
from v2.cloud_functions.cloud_fn_utilities.periodic_maintenance.hourly_maintenance import HourlyMaintenance
from v2.cloud_functions.cloud_fn_utilities.gcp.cloud_env import CloudEnv
from v2.main_app.main_app_utilities.gcp.bucket_manager import BucketManager
from v2.cloud_functions.cloud_fn_utilities.globals import DatastoreKeyTypes
from cloud_fn_utilities.cyber_arena_objects.fixed_arena import FixedArena

fixed_arena = FixedArena

class Test_Daily_Maintence:
    def _init_(self):
        self.env = CloudEnv()
        self.bm = BucketManager()

    def run(self):
        test = DailyMaintenance(debug=True)
        test.run()

if __name__ == "__main__":
    Test_Daily_Maintence().run()