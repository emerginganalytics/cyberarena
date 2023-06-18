from cloud_fn_utilities.gcp.datastore_manager import DataStoreManager
from cloud_fn_utilities.globals import DatastoreKeyTypes, PubSub
from cloud_fn_utilities.gcp.pubsub_manager import PubSubManager
from cloud_fn_utilities.gcp.cloud_env import CloudEnv
from cloud_fn_utilities.state_managers.workout_states import WorkoutStates


class WorkoutBuilder:
    def __init__(self):
        self.env = CloudEnv()
        self.pubsub_manager = PubSubManager(topic=PubSub.Topics.CYBER_ARENA.value, env_dict=self.env.get_env())

    def build_workouts_for_unit(self, unit_id):
        ds_unit = DataStoreManager(key_type=DatastoreKeyTypes.UNIT, key_id=unit_id)
        workouts = ds_unit.get_children(child_key_type=DatastoreKeyTypes.WORKOUT, parent_id=unit_id)
        for workout in workouts:
            workout_id = workout['id']
            if workout.get('state') == WorkoutStates.NOT_BUILT.value:
                student_name = workout.get('student_name', None)
                print(f"Sending job to build workout for {student_name} with workout ID {workout_id}")
                self.pubsub_manager.msg(handler=str(PubSub.Handlers.BUILD.value),
                                        action=str(PubSub.BuildActions.WORKOUT.value),
                                        build_id=workout_id)


if __name__ == '__main__':
    workout_builder = WorkoutBuilder()
    while True:
        unit_id = str(input(f"For what unit ID do you wish to build student workouts? "))
        workout_builder.build_workouts_for_unit(unit_id)

        response = str(input("Do you wish to build workouts for additional units (Y/n)?"))
        if response and str.upper(response) == "N":
            break
