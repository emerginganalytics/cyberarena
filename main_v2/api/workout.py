from api.utilities import auth_required, admin_required, instructor_required
from flask import abort, request, json, session
from flask.views import MethodView
from utilities_v2.gcp.arena_authorizer import ArenaAuthorizer
from utilities_v2.gcp.datastore_manager import DataStoreManager, DatastoreKeyTypes
from utilities_v2.gcp.pubsub_manager import PubSubManager
from utilities_v2.globals import PubSub, BuildConstants
from utilities_v2.gcp.cloud_log import CloudLog

__author__ = "Andrew Bomberger"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Andrew Bomberger"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class WorkoutAPI(MethodView):
    def get(self, build_id=None):
        """Get Workout Object. This endpoint is accessible to all users. Only authenticated users
        can return the full build object"""
        if build_id:
            user_email = session.get('user_email', None)
            user_group = session.get('user_group', None)
            workout = DataStoreManager(
                key_type=DatastoreKeyTypes.CYBERGYM_WORKOUT,
                key_id=build_id).get()
            if workout:
                if user_email == workout['student_email'] or ArenaAuthorizer.UserGroups.AUTHORIZED in user_group:
                    return json.dumps(workout)
                else:
                    # Anonymous user, return only workout state
                    workout_state = workout.get('state', None)
                    if workout_state:
                        return workout_state
                    else:
                        return "RUNNING"
            abort(404)
        # Bad Request; No build_id given
        abort(400)

    @instructor_required
    def post(self):
        """Create Workout"""
        pass

    @auth_required
    def put(self, build_id=None):
        """
        Change build state based on action (START, STOP, NUKE, etc)
        """
        auth_level = session.get('user_groups', None)
        recv_data = request.get_json(force=True)
        action = recv_data.get('action', None)
        run_hours = recv_data.get('time', None)

        # Build_id is supplied. Build type is of either workout or arena type
        if build_id:
            # Get workout from datastore and update run time
            ds_manager = DataStoreManager(key_type=DatastoreKeyTypes.CYBERGYM_WORKOUT, key_id=build_id)
            workout = ds_manager.get()
            if workout:
                # Set new run time
                if run_hours:
                    workout['run_hours'] = min(int(run_hours), 10)
                else:
                    workout['run_hours'] = 2

                # Send PubSub message to start machines
                if action:
                    build_type = workout.get('build_type', None)
                    if build_type:
                        if build_type == BuildConstants.BuildType.ARENA:
                            if ArenaAuthorizer.UserGroups.AUTHORIZED in auth_level:
                                message = f'Cyber Gym Arena {action} Request'
                                if action != "NUKE":
                                    topic_name = PubSub.Topics(f'{action}_ARENA')
                                    ps_manager = PubSubManager(topic=topic_name)
                                    ps_manager.msg(unit_id=build_id, message=message)

                                    # Create Log Event
                                    log_message = "{} action called for Arena {}".format(action, build_id)
                                    CloudLog(
                                        logging_id=CloudLog.LogIDS.API,
                                        severity=CloudLog.LogLevels.INFO
                                    ).create_log(message=log_message, arena=str(build_id), runtime=str(run_hours))
                            # Bad Request; Insufficient Privileges
                            abort(403)
                        else:
                            message = f'Cyber Gym VM {action} Request'
                            if action == "NUKE":
                                topic_name = PubSub.Topics.BUILD_WORKOUTS
                                ps_manager = PubSubManager(topic=topic_name)
                                ps_manager.msg(workout_id=build_id, action=PubSub.WorkoutActions.NUKE)
                            else:
                                topic_name = PubSub.Topics(f'{action}_VM')
                                ps_manager = PubSubManager(topic=topic_name)
                                ps_manager.msg(workout_id=build_id, message=message)

                            # Create Log Event
                            log_message = "{} action called for server {}".format(action, build_id)
                            CloudLog(
                                logging_id=CloudLog.LogIDS.API,
                                severity=CloudLog.LogLevels.INFO
                            ).create_log(message=log_message, workout=str(build_id), runtime=str(run_hours))

                        # Update build and return response
                        ds_manager.put(workout)
                        response = {'status': 200, 'message': f'{recv_data["action"]} workout, {build_id}'}
                        return json.dumps(response)
                else:
                    # Bad request; No action given
                    abort(400)
            else:
                # Bad request; Workout not found
                abort(404)
        else:
            # If no build_id is given, assume unit level vm actions
            # Make sure user is authorized to make request
            if ArenaAuthorizer.UserGroups.AUTHORIZED in auth_level:
                unit_id = recv_data.get('unit_id')
                ds_manager = DataStoreManager(key_id=unit_id)
                workout_list = ds_manager.get_workouts()
                message = f'Cyber Gym VM {action} Request'
                topic_name = PubSub.Topics(f'{action}_VM')
                ps_manager = PubSubManager(topic=topic_name)

                # For each workout in returned query, update run time and publish action
                for workout in workout_list:
                    if run_hours:
                        workout['run_hours'] = min(int(run_hours), 10)
                    else:
                        workout['run_hours'] = 2
                    ds_manager.put(workout)
                    ps_manager.msg(workout_id=workout.key.name, message=message)

                # Create Log Event
                log_message = "{} action called for unit {}".format(action, build_id)
                CloudLog(
                    logging_id=CloudLog.LogIDS.API,
                    severity=CloudLog.LogLevels.INFO
                ).create_log(message=log_message, workout=str(build_id), runtime=str(run_hours))
                # Return response
                return json.dumps({'status': 200, 'message': f'{recv_data["action"]} unit, {build_id}'})
            else:
                # Bad request; Insufficient Privileges
                abort(403)
