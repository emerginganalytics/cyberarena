from cloud_fn_utilities.gcp.datastore_manager import DataStoreManager
from cloud_fn_utilities.gcp.cloud_env import CloudEnv
from cloud_fn_utilities.globals import DatastoreKeyTypes
from cloud_fn_utilities.cyber_arena_objects.unit import Unit

__author__ = "Philip Huff"
__copyright__ = "Copyright 2023, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Production"


class DeleteUnit:
    def __init__(self, unit_id):
        self.unit_id = unit_id
        self.unit = Unit(build_id=unit_id)

    def run(self):
        self.unit.delete()


if __name__ == "__main__":
    response = str(input(f"Which unit do you want to delete? "))
    DeleteUnit(unit_id=response).run()
