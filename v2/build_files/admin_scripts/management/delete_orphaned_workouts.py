import googleapiclient.discovery
from googleapiclient.errors import HttpError
from cloud_fn_utilities.gcp.cloud_env import CloudEnv
from cloud_fn_utilities.gcp.datastore_manager import ServerStates
from cloud_fn_utilities.globals import DatastoreKeyTypes
from google.cloud import datastore
from cloud_fn_utilities.state_managers.server_states import ServerStateManager


def delete_orphaned():
    ds_client = datastore.Client()
    compute = googleapiclient.discovery.build('compute', 'v1')
    env = CloudEnv()

    query_servers = ds_client.query(kind=DatastoreKeyTypes.SERVER)
    query_servers.add_filter('state', '=', 6)
    servers = list(query_servers.fetch())
    query_workout = ds_client.query(kind=DatastoreKeyTypes.WORKOUT)
    workouts = list(query_workout.fetch())
    query_fixed_arena_workspace = ds_client.query(kind=DatastoreKeyTypes.FIXED_ARENA_WORKSPACE)
    workspaces = list(query_fixed_arena_workspace.fetch())

    for server in servers:
        orphaned = None

        if 'parent_build_type' in server.keys():
            if server['parent_build_type'] == 'workout':
                for workout in workouts:
                    if server["parent_id"] == workout["id"]:
                        orphaned = False
                        break
                else:
                    orphaned = True

            elif server['parent_build_type'] == 'fixed_arena_workspace':
                for workspace in workspaces:
                    if 'id' in workspace.keys():
                        if server["parent_id"] == workspace["id"]:
                            orphaned = False
                            break
                    else:
                        if workspace.key.name == server["parent_id"]:
                            orphaned = False
                            break
                else:
                    orphaned = True

        elif 'build_type' in server.keys():
            if server['build_type'] == 'workout':
                for workout in workouts:
                    if server["parent_id"] == workout["id"]:
                        orphaned = False
                        break
                else:
                    orphaned = True

        if orphaned:
            build_id = server.key.name
            state_manager = ServerStateManager(initial_build_id=build_id)
            state_manager.state_transition(ServerStates.DELETING)

            try:
                compute.instances().delete(project=env.project, zone=env.zone,
                                           instance=build_id).execute()
            except HttpError as err:
                state_manager.state_transition(ServerStates.BROKEN)
                continue

            state_manager.state_transition(ServerStates.DELETED)


if __name__ == "__main__":
    print(f"An automated script to delete orphaned workouts")
    delete_orphaned()
