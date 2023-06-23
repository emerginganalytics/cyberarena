from cloud_fn_utilities.gcp.datastore_manager import DataStoreManager
from cloud_fn_utilities.globals import DatastoreKeyTypes, PubSub
from cloud_fn_utilities.gcp.pubsub_manager import PubSubManager
from cloud_fn_utilities.gcp.cloud_env import CloudEnv
from cloud_fn_utilities.state_managers.workout_states import WorkoutStates
from cloud_fn_utilities.cyber_arena_objects.workout import Workout



if __name__ == "__main__":
    env = CloudEnv()
    pubsub_manager = PubSubManager(topic=PubSub.Topics.CYBER_ARENA.value, env_dict=env.get_env())
    workout_id = str(input(f"Which workout ID do you want to rebuild?"))
    ds = DataStoreManager(key_type=DatastoreKeyTypes.WORKOUT, key_id=workout_id)
    workout = ds.get()
    workout['state'] = WorkoutStates.NOT_BUILT.value
    ds.put(workout)
    print(f"Sending job to build workout with workout ID {workout_id}")
    Workout(build_id=workout_id).build()
    # pubsub_manager.msg(handler=str(PubSub.Handlers.BUILD.value), action=str(PubSub.BuildActions.WORKOUT.value),
    #                    build_id=workout_id)
