from cloud_fn_utilities.gcp.pubsub_manager import PubSubManager
from cloud_fn_utilities.globals import PubSub, DatastoreKeyTypes, get_current_timestamp_utc
from cloud_fn_utilities.gcp.compute_manager import ProjectComputeManager
from cloud_fn_utilities.gcp.cloud_env import CloudEnv
from cloud_fn_utilities.database.vulnerabilities import Vulnerabilities
from cloud_fn_utilities.cyber_arena_objects.vulnerabilities import Vulnerabilities
from cloud_fn_utilities.gcp.datastore_manager import DataStoreManager
from cloud_fn_utilities.send_mail.send_mail import SendMail

__author__ = "Philip Huff"
__copyright__ = "Copyright 2023, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff, Ryan Ebsen, Bryce Ebsen"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Production"


class DailyMaintenance:
    def __init__(self, debug=False, env_dict=None):
        self.env = CloudEnv(env_dict=env_dict) if env_dict else CloudEnv()
        self.compute_manager = ProjectComputeManager(env_dict=self.env.get_env())
        self.pub_sub_mgr = PubSubManager(PubSub.Topics.CYBER_ARENA, env_dict=self.env.get_env())
        self.debug = debug
        self.ds = DataStoreManager(key_type=DatastoreKeyTypes.UNIT)

    def run(self):
        self._stop_all()
        self._notify_expiring_units()
        Vulnerabilities().update()

    def _stop_all(self):
        self.compute_manager.stop_everything()

    def _notify_expiring_units(self):
        """
        sends an email to the owner of all units that expire within 48 hours
        @return:
        """
        expiring_units = self.ds.get_expiring_units()
        for unit_id in expiring_units:
            unit = self.ds.get(key_type=DatastoreKeyTypes.UNIT, key_id=unit_id)
            workout_name = unit['summary']['name']
            instructor = unit['instructor_id']
            num_workouts = len(unit['servers'])
            expires = unit['workspace_settings']['expires']
            hours_until_expired = round((expires - get_current_timestamp_utc()) / 3600)
            SendMail().send_expiring_units(unit_id=unit_id, workout_name=workout_name, instructor=instructor,
                                           num_workouts=num_workouts, hours_until_expires=hours_until_expired)
