from cloud_fn_utilities.gcp.datastore_manager import DataStoreManager
from cloud_fn_utilities.gcp.cloud_env import CloudEnv
from cloud_fn_utilities.globals import DatastoreKeyTypes


__author__ = "Philip Huff"
__copyright__ = "Copyright 2023, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Production"


class ListWorkouts:
    def __init__(self, unit_id):
        self.unit_id = unit_id
        self.ds = DataStoreManager(key_type=DatastoreKeyTypes.UNIT, key_id=self.unit_id)
        self.env = CloudEnv()

    def run(self):
        workouts = self.ds.get_children(child_key_type=DatastoreKeyTypes.WORKOUT, parent_id=self.unit_id)
        for workout in workouts:
            print(f"{self.env.main_app_url}/student/assignment/workout/{workout.key.name}")


if __name__ == "__main__":
    response = str(input(f"Which unit do you want to list? "))
    ListWorkouts(unit_id=response).run()