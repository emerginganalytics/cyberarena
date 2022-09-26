from cloud_fn_utilities.gcp.pubsub_manager import PubSubManager
from cloud_fn_utilities.globals import PubSub, FixedArenaClassStates
from cloud_fn_utilities.state_managers.fixed_arena_states import FixedArenaStateManager
from cloud_fn_utilities.gcp.compute_manager import ComputeManager

from cloud_fn_utilities.cyber_arena_objects.fixed_arena_class import FixedArenaClass


class DailyMaintenance:
    def __init__(self, debug=False):
        self.debug = debug
        self.pub_sub_mgr = PubSubManager(PubSub.Topics.CYBER_ARENA)
        self.fa_state_manager = FixedArenaStateManager()

    def run(self):
        self._stop_all()

    def _stop_all(self):
        running_classes = self.fa_state_manager.get_running()
        for fixed_arena_class in running_classes:
            fac_state = fixed_arena_class.get('state', None)
            if not fac_state:
                FixedArenaClass(build_id=fixed_arena_class.key.name).mark_broken()
                continue

            if fac_state not in [FixedArenaClassStates.BROKEN.value, FixedArenaClassStates.DELETED.value]:
                build_id = fixed_arena_class.key.name
                if self.debug:
                    ComputeManager(server_name=build_id).stop()
                else:
                    self.pub_sub_mgr.msg(handler=PubSub.Handlers.CONTROL,
                                         cyber_arena_object=str(PubSub.CyberArenaObjects.FIXED_ARENA_CLASS.value),
                                         build_id=build_id, action=str(PubSub.Actions.STOP.value))

    def delete_expired(self):
        pass
