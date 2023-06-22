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


def delete_units(units):
	for unit in units:
		Unit(build_id=unit).delete()


if __name__=='__main__':
	units = ['qjgiidaofz', 'qjgiidaofz', 'zsonwdikbp', 'gpkobefmvw', 'lrisljjkbg', 'ryoxidbtco', 'wkavcidzbs']
	delete_units(units)
