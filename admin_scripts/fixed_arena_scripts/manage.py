from fixed_arena_scripts.test_delete_fixed_arena_class import TestFixedArenaDelete
from fixed_arena_scripts.test_v2_fixed_arena import TestFixedArena
from fixed_arena_scripts.test_v2_fixed_arena_class import TestFixedArenaWorkout
from main_app_utilities.globals import PubSub


class ManageFixedArena:
    def __init__(self, build_id):
        self.build_id = build_id

    def rebuild_arena(self):
        self.delete_fixed_arena()
        TestFixedArena().build()

    @staticmethod
    def delete_fixed_arena(self):
        TestFixedArenaDelete().run()

    def manage_class(self, action):
        if action == PubSub.Actions.STOP.name:
            TestFixedArenaWorkout().stop()
        elif action == PubSub.Actions.START.name:
            TestFixedArenaWorkout().start()
        elif action == PubSub.Actions.BUILD.name:
            TestFixedArenaWorkout().build()


if __name__ == '__main__':
    actions = [PubSub.Actions.BUILD.name, PubSub.Actions.START.name, PubSub.Actions.STOP.name]
    build_id = 'cln-stoc'
    ManageFixedArena(build_id=build_id).rebuild_arena()

    # ManageFixedArena(build_id=build_id).manage_class(action=actions[0])
