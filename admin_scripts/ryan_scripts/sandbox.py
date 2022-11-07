from cloud_fn_utilities.gcp.datastore_manager import DataStoreManager
from cloud_fn_utilities.globals import PubSub, DatastoreKeyTypes
from cloud_fn_utilities.state_managers.fixed_arena_states import FixedArenaStateManager
from cloud_fn_utilities.state_managers.server_states import ServerStateManager
from cloud_fn_utilities.periodic_maintenance.quarter_hourly_maintenance import QuarterHourlyMaintenance
from cloud_fn_utilities.gcp.pubsub_manager import PubSubManager

def testGetExpired():
    matinance = QuarterHourlyMaintenance()
    matinance.run()

if __name__ == "__main__":
    testGetExpired()
