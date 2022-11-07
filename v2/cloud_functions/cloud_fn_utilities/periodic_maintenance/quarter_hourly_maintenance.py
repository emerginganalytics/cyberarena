from cloud_fn_utilities.globals import PubSub, DatastoreKeyTypes
from cloud_fn_utilities.gcp.pubsub_manager import PubSubManager
from cloud_fn_utilities.gcp.compute_manager import ComputeManager
from cloud_fn_utilities.gcp.datastore_manager import DataStoreManager
from cloud_fn_utilities.state_managers.server_states import ServerStateManager

__author__ = "Philip Huff"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff, Ryan Ebsen"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class QuarterHourlyMaintenance:
    def __init__(self, debug=False):
        self.debug = debug
        self.ds = DataStoreManager(key_type=DatastoreKeyTypes.SERVER)
        self.pub_sub_mgr = PubSubManager(PubSub.Topics.CYBER_ARENA)
        self.server_state_manager = ServerStateManager()

    def run(self):
        self._stop_lapsed()

    def _stop_lapsed(self):
        lapsed = self.server_state_manager.get_expired()
        to_stop = []
        for server in lapsed:
            if server['parent_id']:
                to_stop.append(server['parent_id'] + '-' + server['name'])
            else:
                to_stop.append(server['name'])

        for server in to_stop:
            if self.debug:
                ComputeManager(server_name=server).stop()
            else:
                self.pub_sub_mgr.msg(handler=PubSub.Handlers.CONTROL,
                                     cyber_arena_object=str(PubSub.CyberArenaObjects.SERVER.value),
                                     build_id=server, action=str(PubSub.Actions.STOP.value))
