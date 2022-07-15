from api.decorators import auth_required, admin_required
from flask import abort, request, json, session
from flask.views import MethodView
from utilities.gcp.arena_authorizer import ArenaAuthorizer
from utilities.gcp.datastore_manager import DataStoreManager, DatastoreKeyTypes
from utilities.gcp.pubsub_manager import PubSubManager
from utilities.globals import PubSub

__author__ = "Andrew Bomberger"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Andrew Bomberger"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class Workout(MethodView):
    def get(self, build_id=None):
        """Get Workout Object. This endpoint is accessible to all users. Only authenticated users
        can return the full build object"""
        if build_id:
            user_email = session.get('user_email', None)
            user_group = session.get('user_group', None)
            workout = DataStoreManager(
                key_type=DatastoreKeyTypes.CYBERGYM_WORKOUT.value,
                key_id=build_id).get()
            if workout:
                if user_email and workout['registration_required']:
                    if user_email == workout['student_email'] or ArenaAuthorizer.UserGroups.AUTHORIZED in user_group:
                        return json.dumps(workout)
                    # Bad Request; Unauthorized User
                    else:
                        abort(403)
                else:
                    # Anonymous user, return only workout state
                    workout_state = workout.get('state', None)
                    if workout_state:
                        return workout_state
                    else:
                        return "RUNNING"
            # Bad Request; Workout not found
            abort(404)
        # Bad Request; No build_id given
        abort(400)

    @auth_required
    def post(self, build_id):
        """Create Workout"""
        if build_id:
            workout = DataStoreManager(key_type=DatastoreKeyTypes.CYBERGYM_WORKOUT.value, key_id=build_id).get()
            if workout['state'] == 'READY':
                data = request.json
                workout_id = data.get('workout_id', None)
                # No workout_id given
                if not workout_id:
                    abort(404)
                ps_manager = PubSubManager(topic=PubSub.Topics.BUILD_WORKOUTS.value)
                message = f"Student initiated cloud build for workout {workout_id}"
                ps_manager.msg(workout_id=workout_id, message=message)
                return 'Workout Built'
            # Bad Request; Already Built
            else:
                abort(400)
        else:
            auth_level = session.get('user_groups', None)
            if ArenaAuthorizer.UserGroups.AUTHORIZED in auth_level:
               # TODO: Write logic to support standard workout creation requests
                return '200'
            # Invalid Request; Insufficient Permissions
            else:
                abort(403)

    @admin_required
    def delete(self):
        abort(405)

    def put(self, build_id=None):
        """
        Change build state based on action (START, STOP, NUKE, etc)
        """
        auth_level = session.get('user_groups', None)
        recv_data = request.json
        action = recv_data.get('action', None)
        # TODO: Move calculating run_hours to function that is called by PubSub request.
        #       This will allow us to remove all datastore queries out of this method
        run_hours = recv_data.get('time', None)
        if action:
            # Build_id is supplied. Build type is of either workout or arena type
            if build_id:
                # Request is sent to start a specific server
                if recv_data.get('manage_server', False):
                    server_name = recv_data.get('server_name', None)
                    PubSubManager(topic=PubSub.Topics.MANAGE_SERVER).msg(
                        action=action, server_name=server_name)
                else:
                    ds_manager = DataStoreManager(key_type=DatastoreKeyTypes.CYBERGYM_WORKOUT.value, key_id=build_id)
                    workout = ds_manager.get()
                    if workout:
                        if run_hours:
                            workout['run_hours'] = min(int(run_hours), 10)
                        else:
                            workout['run_hours'] = 2
                        if action == PubSub.WorkoutActions.NUKE.value:
                            topic_name = PubSub.Topics.BUILD_WORKOUTS.value
                        else:
                            topic_name = PubSub.Topics[f'{action}_VM'].value
                        PubSubManager(topic=topic_name).msg(workout_id=build_id, action=action, data=recv_data)
                        ds_manager.put(workout)
                        response = {'status': 200, 'message': f'{action} workout, {build_id}'}
                        return json.dumps(response)
                    else:
                        # Bad request; Workout not found
                        abort(404)
            else:
                # If no build_id is given, assumed unit level vm actions
                # Make sure user is authorized to make request
                if ArenaAuthorizer.UserGroups.AUTHORIZED in auth_level:
                    unit_id = recv_data.get('unit_id')
                    ds_manager = DataStoreManager(key_id=unit_id)
                    if action == PubSub.WorkoutActions.NUKE.value:
                        topic_name = PubSub.Topics.BUILD_WORKOUTS.value
                    else:
                        topic_name = PubSub.Topics[f'{action}_VM'].value
                    ps_manager = PubSubManager(topic=topic_name)

                    # For each workout in returned query, update run time and publish action
                    for workout in ds_manager.get_workouts():
                        if run_hours:
                            workout['run_hours'] = min(int(run_hours), 10)
                        else:
                            workout['run_hours'] = 2
                        ds_manager.put(workout)
                        ps_manager.msg(workout_id=workout.key.name, action=action, data=recv_data)
                    return json.dumps({'status': 200, 'message': f'{recv_data["action"]} unit, {build_id}'})
                else:
                    # Bad request; Insufficient Privileges
                    abort(403)
        else:
            abort(400)
