from cloud_fn_utilities.gcp.pubsub_manager import PubSubManager
from cloud_fn_utilities.globals import PubSub, FixedArenaClassStates
from cloud_fn_utilities.state_managers.fixed_arena_states import FixedArenaStateManager
import time

from cloud_fn_utilities.cyber_arena_objects.fixed_arena_class import FixedArenaClass

__author__ = "Philip Huff"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class HourlyMaintenance:
    def __init__(self, debug=False):
        self.debug = debug
        self.pub_sub_mgr = PubSubManager(PubSub.Topics.CYBER_ARENA)
        self.fa_state_manager = FixedArenaStateManager()

    def delete_expired(self):
        expired_classes = self.fa_state_manager.get_expired()
        for fixed_arena_class in expired_classes:
            fac_state = fixed_arena_class.get('state', None)
            if not fac_state:
                FixedArenaClass(build_id=fixed_arena_class.key.name).mark_broken()
                continue

            if fac_state not in [FixedArenaClassStates.BROKEN.value, FixedArenaClassStates.DELETED.value]:
                build_id = fixed_arena_class.key.name
                if self.debug:
                    FixedArenaClass(build_id=build_id, debug=self.debug).delete()
                else:
                    self.pub_sub_mgr.msg(handler=PubSub.Handlers.CONTROL,
                                         cyber_arena_object=str(PubSub.CyberArenaObjects.FIXED_ARENA_CLASS.value),
                                         build_id=build_id, action=str(PubSub.Actions.DELETE.value))
