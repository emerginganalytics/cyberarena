#
# This function is intended to be run in Google Cloud Functions as the handler to the maintenance pub/sub topic
#
import calendar
import time
from common.dns_functions import delete_dns
from common.compute_management import server_delete
from common.globals import ArenaWorkoutDeleteType, BUILD_STATES, compute, cloud_log, ds_client, gcp_operation_wait, \
    LOG_LEVELS, LogIDs, project, PUBSUB_TOPICS, region, SERVER_ACTIONS,  WORKOUT_TYPES, zone
from common.start_vm import state_transition
from datetime import datetime
from googleapiclient.errors import HttpError
from google.cloud import pubsub_v1


class DeletionManager:
    """
    Handles all resource deletion requests related to workouts both individual and arena types.

    Once a workout is declared as expired via exceeding the build duration defined by the instructor during initial
    build time, the build_id (workout_id or unit_id depending on build_type) is published to the maintaining topic which
    triggers the deletion process for that specific build.

    Resource deletion is organized in levels of states defined in common.globals.BUILD_STATES. For both workout build
    types (individual and arena), the deletion process must be initiated in the following order:
        DNS, servers, firewall, routes, subnetworks, and finally networks.
    Individual and Arena workouts are different only in that Arenas have states at both the unit and workout level that
    need to be validated.

    The only exception to the deletion process as stated above is container based workouts. Since these are typically
    centered around a Cloud Run application, we only need to set the Datastore state for that workout as DELETED so that
    the workout doesn't appear again in future queries. No other resources are required to be deleted.

    This class is intended to be consumed through cloud_fn_delete_expired_workout and tied to a pubsub topic
    triggered by a cloud scheduler to run every 15 minutes or more.
    """
    # Number of seconds in a month
    DEFAULT_LOOKBACK = 10512000
    # The type of deletion to process
    class DeletionType:
        EXPIRED = "Expired"
        ALL = "All"
        SPECIFIC = "Specific"
        CLEANUP = "Cleanup"
        MISFIT = "misfit"

    def __init__(self, deletion_type=DeletionType.EXPIRED, build_id=None, build_type=WORKOUT_TYPES.WORKOUT,
                 lookback_seconds=DEFAULT_LOOKBACK, debug=False):
        self.deletion_type = deletion_type
        self.build_id = build_id
        self.build_type = build_type
        self.lookback_seconds = lookback_seconds
        self.debug = debug

    def run(self, deletion_type=None, debug=False):
        """
        Runs the deletion job based on the parameters passed into the init function
        @return:
        @rtype:
        """
        if deletion_type:
            self.deletion_type = deletion_type

        if self.deletion_type == self.DeletionType.EXPIRED:
            if self.build_type == WORKOUT_TYPES.WORKOUT:
                self._delete_expired_workouts()
            elif self.build_type == WORKOUT_TYPES.ARENA:
                self._delete_expired_arenas()
        elif self.deletion_type == self.DeletionType.MISFIT:
            self._delete_misfits(misfit_type=WORKOUT_TYPES.WORKOUT)
            self._delete_misfits(misfit_type=WORKOUT_TYPES.ARENA)
        elif self.deletion_type == self.DeletionType.CLEANUP:
            self._delete_all_subnetworks()
            self._delete_orphaned_networks()
        elif self.deletion_type == self.DeletionType.SPECIFIC:
            if self.build_type == WORKOUT_TYPES.WORKOUT:
                self._delete_specific_workout()
            elif self.build_type == WORKOUT_TYPES.ARENA:
                self._delete_specific_arena()
        elif self.deletion_type == ArenaWorkoutDeleteType.SERVER:
            self._delete_vms()
        elif self.deletion_type == ArenaWorkoutDeleteType.NETWORK:
            self._delete_network()
        elif self.deletion_type == ArenaWorkoutDeleteType.ROUTES:
            self._delete_routes()
        elif self.deletion_type == ArenaWorkoutDeleteType.FIREWALL_RULES:
            self._delete_firewall_rules()
        return True

    def _delete_expired_workouts(self):
        """
        Queries the data store for workouts which have expired. Workout expiration is defined during the build
        process based on the number of days an instructor needs the workout to be available. Resources to delete include
        servers, networks, routes, firewall-rules and DNS names. The deletion of resources is based on a unique
        identifier for the workout. Every built resource uses this for a prefix.
        Deletion must occur in a given order with networks being deleted last.

        This function is intended to be consumed through cloud_fn_delete_expired_workout and tied to a pubsub topic
        triggered by a cloud scheduler to run every 15 minutes or more.
        :return: None
        """
        query_old_workouts = ds_client.query(kind='cybergym-workout')
        query_old_workouts.add_filter('active', '=', True)

        for workout in list(query_old_workouts.fetch()):
            workout_project = workout.get('build_project_location', project)
            if workout_project == project:
                if 'state' not in workout:
                    workout['state'] = BUILD_STATES.DELETED
                container_type = False
                # If the workout is a container, then expire the container so it does not show up in the list of running workouts.
                if 'build_type' in workout and workout['build_type'] == 'container':
                    container_type = True
                    if 'timestamp' not in workout or 'expiration' not in workout and \
                            workout['state'] != BUILD_STATES.DELETED:
                        state_transition(workout, BUILD_STATES.DELETED)
                    elif self._workout_age(workout['timestamp']) >= int(workout['expiration']) and \
                            workout['state'] != BUILD_STATES.DELETED:
                        state_transition(workout, BUILD_STATES.DELETED)

                arena_type = False
                if 'build_type' in workout and workout['build_type'] == 'arena' or \
                        'type' in workout and workout['type'] == 'arena':
                    arena_type = True

                if not container_type and not arena_type:
                    if self._workout_age(workout['timestamp']) >= int(workout['expiration']):
                        if workout['state'] != BUILD_STATES.DELETED:
                            state_transition(workout, BUILD_STATES.READY_DELETE)
                            workout_id = workout.key.name
                            # Delete the workouts asynchronously
                            pubsub_topic = PUBSUB_TOPICS.DELETE_EXPIRED
                            publisher = pubsub_v1.PublisherClient()
                            topic_path = publisher.topic_path(project, pubsub_topic)
                            publisher.publish(topic_path, data=b'Workout Delete', workout_type=WORKOUT_TYPES.WORKOUT,
                                              workout_id=workout_id)

    def _delete_expired_arenas(self):
        """
        It is common for cloud functions to time out when deleting several workouts. This adds an additional work thread
        to delete arenas similar to the delete_workouts() function
        :return:
        """
        query_old_units = ds_client.query(kind='cybergym-unit')
        query_old_units.add_filter("timestamp", ">", str(calendar.timegm(time.gmtime()) - self.lookback_seconds))
        for unit in list(query_old_units.fetch()):
            arena_type = False
            if 'build_type' in unit and unit['build_type'] == 'arena':
                arena_type = True

            if arena_type:
                try:
                    unit_state = unit.get('state', None)
                    unit_deleted = True if not unit_state or unit_state == BUILD_STATES.DELETED else False
                    if self._workout_age(unit['timestamp']) >= int(unit['expiration']) \
                            and not unit_deleted:
                        state_transition(unit, BUILD_STATES.READY_DELETE)
                        pubsub_topic = PUBSUB_TOPICS.DELETE_EXPIRED
                        publisher = pubsub_v1.PublisherClient()
                        topic_path = publisher.topic_path(project, pubsub_topic)
                        publisher.publish(topic_path, data=b'Workout Delete', workout_type=WORKOUT_TYPES.ARENA,
                                          unit_id=unit.key.name)
                except KeyError:
                    state_transition(unit, BUILD_STATES.DELETED)
        cloud_log("delete_arenas", f"Deleted expired arenas", LOG_LEVELS.INFO)

    def _delete_misfits(self, misfit_type):
        """
        Periodically a build will fail to build the complete workout. This results in what is defined as a misfit and
        is unusable at that point.
        @param misfit_type: Either workout or arena
        @type misfit_type: String
        @return:
        @rtype:
        """
        pubsub_topic = PUBSUB_TOPICS.DELETE_EXPIRED
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(project, pubsub_topic)
        query_kind = 'cybergym-unit' if misfit_type == WORKOUT_TYPES.ARENA else 'cybergym-workout'
        query_misfits = ds_client.query(kind=query_kind)
        query_misfits.add_filter('misfit', '=', True)
        for build in list(query_misfits.fetch()):
            workout_project = build.get('build_project_location', project)
            if workout_project == project:
                build_id = build.key.name
                is_misfit = build.get('misfit', False)
                current_state = build.get('state', None)
                if current_state != BUILD_STATES.DELETED:
                    if misfit_type == WORKOUT_TYPES.ARENA:
                        state_transition(build, BUILD_STATES.READY_DELETE)
                        publisher.publish(topic_path, data=b'Workout Delete', workout_type=WORKOUT_TYPES.ARENA,
                                          unit_id=build_id)

                    elif misfit_type == WORKOUT_TYPES.WORKOUT:
                        state_transition(build, BUILD_STATES.READY_DELETE)
                        if self.debug:
                            dm = DeletionManager(deletion_type=DeletionManager.DeletionType.SPECIFIC,
                                                 build_id=build_id, build_type=WORKOUT_TYPES.WORKOUT, debug=True)
                            dm.run()
                        else:
                            publisher.publish(topic_path, data=b'Workout Delete', workout_type=WORKOUT_TYPES.WORKOUT,
                                              workout_id=build_id)
        cloud_log(LogIDs.DELETION_MANAGEMENT, f"PubSub commands sent to delete misfit {misfit_type}", LOG_LEVELS.INFO)

    def _delete_specific_workout(self):
        """
        Delete all resources in a specific workout. This is called as a cloud function
        @return: None
        @rtype:
        """
        workout = ds_client.get(ds_client.key('cybergym-workout', self.build_id))
        if not workout:
            return False
        cloud_log(self.build_id, f"Deleting workout {self.build_id}", LOG_LEVELS.INFO)
        if 'state' in workout:
            if workout['state'] in [BUILD_STATES.READY, BUILD_STATES.RUNNING]:
                state_transition(workout, BUILD_STATES.DELETING_SERVERS)
            elif workout['state'] == BUILD_STATES.DELETED:
                return False
        self._delete_vms()
        if self._wait_for_deletion(wait_type=ArenaWorkoutDeleteType.SERVER):
            if self._delete_firewall_rules():
                self._wait_for_deletion(wait_type=ArenaWorkoutDeleteType.FIREWALL_RULES)
                if self._delete_routes():
                    if self._delete_subnetworks():
                        self._wait_for_deletion(wait_type=ArenaWorkoutDeleteType.SUBNETWORK)
                        if self._delete_network():
                            state_transition(workout, BUILD_STATES.DELETED)
                            cloud_log(self.build_id, f"Finished deleting workout{self.build_id}", LOG_LEVELS.INFO)
                            if workout['misfit']:
                                ds_client.delete(workout.key)
                            return True
        cloud_log(self.build_id, f"There was a problem deleting workout {self.build_id}", LOG_LEVELS.ERROR)
        return False

    def _delete_specific_arena(self):
        """
        Arenas are unique in having both resources at the unit level and individual workout resources. This
        function addresses those differences
        :param arena_id: The Unit_ID of this arena
        :return:
        """
        unit = ds_client.get(ds_client.key('cybergym-unit', self.build_id))
        cloud_log(self.build_id, f"Deleting arena {self.build_id}", LOG_LEVELS.INFO)
        try:
            # Arena external_ip is tied to <unit_id>_student_entry server.
            # We need to query that entity in order to delete the proper DNS record
            query_student_entry_server = ds_client.query(kind='cybergym-server')
            query_student_entry_server.add_filter("workout", "=", self.build_id)
            unit_server = list(query_student_entry_server.fetch())
            if unit_server:
                delete_dns(self.build_id, unit_server[0]["external_ip"])
        except HttpError:
            cloud_log(self.build_id, f"DNS record does not exist for arena {self.build_id}", LOG_LEVELS.WARNING)
            pass
        except KeyError:
            cloud_log(self.build_id, f"No external IP address for arena {self.build_id}", LOG_LEVELS.WARNING)
            pass
        pubsub_topic = PUBSUB_TOPICS.DELETE_EXPIRED
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(project, pubsub_topic)
        for workout_id in unit['workouts']:
            # For each student arena server, publish message with workout_id to delete that instance
            publisher.publish(topic_path, data=b'Workout Delete', workout_type=WORKOUT_TYPES.ARENA,
                              workout_id=workout_id, arena_workout_delete_type=ArenaWorkoutDeleteType.SERVER)
        # Only student guacamole server remains. Publish message using build_id (arena unit_id)
        publisher.publish(topic_path, data=b'Workout Delete', workout_type=WORKOUT_TYPES.ARENA,
                          workout_id=self.build_id, arena_workout_delete_type=ArenaWorkoutDeleteType.SERVER)
        time.sleep(60)
        # Now delete all of the network elements
        self._delete_firewall_rules()
        for workout_id in unit['workouts']:
            publisher.publish(topic_path, data=b'Workout Delete', workout_type=WORKOUT_TYPES.ARENA,
                              workout_id=workout_id,
                              arena_workout_delete_type=ArenaWorkoutDeleteType.FIREWALL_RULES)
        time.sleep(30)
        self._delete_routes()
        self._delete_subnetworks()
        for workout_id in unit['workouts']:
            publisher.publish(topic_path, data=b'Workout Delete', workout_type=WORKOUT_TYPES.ARENA,
                              workout_id=workout_id,
                              arena_workout_delete_type=ArenaWorkoutDeleteType.ROUTES)
        time.sleep(30)
        self._delete_network()
        for workout_id in unit['workouts']:
            publisher.publish(topic_path, data=b'Workout Delete', workout_type=WORKOUT_TYPES.ARENA,
                              workout_id=workout_id,
                              arena_workout_delete_type=ArenaWorkoutDeleteType.NETWORK)
        return True

    def _delete_vms(self):
        """
        Send pubsub message for asynchronous deletion of all workout machines.

        By default it filters available instances based on self.build_id however for arena builds,
        it is necessary to pass in value, workout_id as self.build_id is the unit_id for the arena.
        """
        query_workout_servers = ds_client.query(kind='cybergym-server')
        cloud_log(self.build_id, f"Deleting computing resources for build {self.build_id}", LOG_LEVELS.INFO)
        query_workout_servers.add_filter("workout", "=", self.build_id)

        for server in list(query_workout_servers.fetch()):
            # Publish to a server management topic
            if self.debug:
                server_delete(server_name=server['name'])
            else:
                pubsub_topic = PUBSUB_TOPICS.MANAGE_SERVER
                publisher = pubsub_v1.PublisherClient()
                topic_path = publisher.topic_path(project, pubsub_topic)
                future = publisher.publish(topic_path, data=b'Server Delete', server_name=server['name'],
                                           action=SERVER_ACTIONS.DELETE)
                print(future.result())

    def _delete_firewall_rules(self):
        cloud_log(self.build_id, f"Deleting firewall for workout {self.build_id}", LOG_LEVELS.INFO)

        try:
            result = compute.firewalls().list(project=project, filter='name = {}*'.format(self.build_id)).execute()
            if 'items' in result:
                for fw_rule in result['items']:
                    response = compute.firewalls().delete(project=project, firewall=fw_rule["name"]).execute()
                try:
                    compute.globalOperations().wait(project=project, operation=response["id"]).execute()
                except HttpError:
                    cloud_log(self.build_id, f"Error in waiting for firewall rule deletion", LOG_LEVELS.WARNING)
                    pass
            return True
        except():
            cloud_log(self.build_id, f"Error in deleting firewall rules for workout {self.build_id}", LOG_LEVELS.ERROR)
            return False

    def _delete_routes(self):
        cloud_log(self.build_id, f"Deleting routes for workout {self.build_id}", LOG_LEVELS.INFO)

        result = compute.routes().list(project=project, filter='name = {}*'.format(self.build_id)).execute()
        if 'items' in result:
            for route in result['items']:
                response = compute.routes().delete(project=project, route=route["name"]).execute()
                try:
                    compute.globalOperations().wait(project=project, operation=response["id"]).execute()
                except HttpError:
                    cloud_log(self.build_id, f"Timeout when deleting routes for {self.build_id}", LOG_LEVELS.ERROR)
                    return False
        return True

    def _delete_subnetworks(self):
        i = 0
        result = compute.subnetworks().list(project=project, region=region, filter=f'name = {self.build_id}*').execute()
        if 'items' in result:
            while i < 6:
                try:
                    for subnetwork in result['items']:
                        response = compute.subnetworks().delete(project=project, region=region,
                                                                subnetwork=subnetwork["name"]).execute()
                    try:
                        compute.regionOperations().wait(project=project, region=region, operation=response["id"]).execute()
                    except HttpError as err:
                        pass
                    return True
                except HttpError:
                    time.sleep(5)
                    i += 1
                    pass
        else:
            # Return true since the subnetwork has been deleted
            return True
        cloud_log(self.build_id, f"Error in deleting subnetwork for workout {self.build_id}", LOG_LEVELS.ERROR)
        return False

    def _delete_network(self):
        i = 0
        # Now it is safe to delete the networks.
        success = True
        result = compute.networks().list(project=project, filter=f'name = {self.build_id}*').execute()
        if 'items' in result:
            for network in result['items']:
                # Networks are not being deleted because the operation occurs too fast.
                response = compute.networks().delete(project=project, network=network["name"]).execute()
                if not gcp_operation_wait(service=compute, response=response, wait_type="global"):
                    cloud_log("cybergym-app", f"Timeout waiting for network {network['name']} to delete",
                              LOG_LEVELS.WARNING)
                    success = False
                else:
                    # For workouts with multiple networks, avoid setting success to true if at least one
                    # network has an error.
                    if not success:
                        success = True
        else:
            # Return true since the network has already been deleted
            return True

        if success:
            self._process_workout_deletion()
            return True
        else:
            return False

    @staticmethod
    def _delete_orphaned_networks():
        """
        This function iterates through all of the networks and deletes any networks which do not have corresponding
        subnetworks. This operation is safe because all active workouts will have a subnetwork.
        :returns: True if the operations was successful. Otherwise, this returns false.
        """
        networks = compute.networks().list(project=project).execute()
        if 'items' in networks:
            for network in networks['items']:
                if 'subnetworks' not in network:
                    cloud_log("cybergym-app", f"Deleting orphaned network {network['name']}", LOG_LEVELS.INFO)
                    try:
                        response = compute.networks().delete(project=project, network=network["name"]).execute()
                    except HttpError:
                        cloud_log("cybergym-app", f"Error deleting network {network['name']}", LOG_LEVELS.ERROR)
                    if not gcp_operation_wait(service=compute, response=response, wait_type="global"):
                        cloud_log("cybergym-app", f"Timeout waiting for network {network['name']} to delete",
                                  LOG_LEVELS.WARNING)
                        pass
        else:
            return False
        return True

    @staticmethod
    def _delete_all_subnetworks():
        """
        This function iterates through all of the networks and deletes any networks which do not have corresponding
        subnetworks. This operation is safe because all active workouts will have a subnetwork.
        :returns: True if the operations was successful. Otherwise, this returns false.
        """
        subnetworks = compute.subnetworks().list(project=project, region=region).execute()
        if 'items' in subnetworks:
            for subnetwork in subnetworks['items']:
                if not subnetwork['name'].startswith('cyber') and not subnetwork['name'].startswith('default'):
                    cloud_log("cybergym-app", f"Deleting subnetwork {subnetwork['name']}", LOG_LEVELS.INFO)
                    try:
                        response = compute.subnetworks().delete(project=project, region=region,
                                                                subnetwork=subnetwork["name"]).execute()
                    except HttpError:
                        cloud_log("cybergym-app", f"Error deleting network {subnetwork['name']}", LOG_LEVELS.ERROR)
                        break
                    if not gcp_operation_wait(service=compute, response=response, wait_type="region"):
                        cloud_log("cybergym-app", f"Timeout waiting for network {subnetwork['name']} to delete",
                                  LOG_LEVELS.WARNING)
                    pass
        else:
            return False
        return True

    def _workout_age(self, created_date):
        now = datetime.now()
        instance_creation_date = datetime.fromtimestamp(int(created_date))
        delta = now - instance_creation_date
        return delta.days

    def _wait_for_deletion(self, wait_type=ArenaWorkoutDeleteType.SERVER):
        """
        For asynchronous deletion, wait until all jobs have completed.
        @param build_id: The id of the build to use in searching for resources
        @type build_id: String
        @param wait_type: designated type of resource
        @type wait_type: String
        @return: Status
        @rtype: Boolean
        """
        i = 0
        all_deleted = False
        while not all_deleted and i < 10:
            if wait_type == ArenaWorkoutDeleteType.SERVER:
                result = compute.instances().list(project=project, zone=zone, filter=f"name = {self.build_id}*").execute()
            elif wait_type == ArenaWorkoutDeleteType.ROUTES:
                result = compute.routes().list(project=project, filter=f"name = {self.build_id}*").execute()
            elif wait_type == ArenaWorkoutDeleteType.FIREWALL_RULES:
                result = compute.firewalls().list(project=project, filter=f"name = {self.build_id}*").execute()
            elif wait_type == ArenaWorkoutDeleteType.NETWORK:
                result = compute.networks().list(project=project, filter=f"name = {self.build_id}*").execute()
            elif wait_type == ArenaWorkoutDeleteType.SUBNETWORK:
                result = compute.subnetworks().list(project=project, region=region,
                                                    filter=f"name = {self.build_id}*").execute()
            if 'items' not in result:
                all_deleted = True
            else:
                i += 1
                time.sleep(10)
        return all_deleted

    def _process_workout_deletion(self):
        """
        Since workouts are deleted asynchronously, this functions is called when the last step of workout deletion
        occurs.
        @param workout_id: The ID of the workout to query
        @type workout_id: String
        @return: None
        @rtype: None
        """
        if self.build_type == WORKOUT_TYPES.ARENA:
            unit = ds_client.get(ds_client.key('cybergym-unit', self.build_id))
            all_workouts_deleted = True
            if unit:
                is_misfit = unit['arena'].get('misfit', None)
                # validate deletion state for student arena servers
                for workout_id in unit['workouts']:
                    query_workout_servers = ds_client.query(kind='cybergym-server')
                    query_workout_servers.add_filter("workout", "=", workout_id)
                    server_list = list(query_workout_servers.fetch())
                    for server in server_list:
                        workout_state = server['state']
                        if workout_state != BUILD_STATES.DELETED:
                            all_workouts_deleted = False
                # validate deletion state for student entry server
                query_unit_server = ds_client.query(kind='cybergym-server')
                query_unit_server.add_filter("workout", "=", self.build_id)
                unit_server = list(query_unit_server.fetch())
                student_entry_state = unit_server[0]['state']
                if student_entry_state != BUILD_STATES.DELETED:
                    all_workouts_deleted = False
                # if all machines have DELETED state, update arena state to DELETED
                if all_workouts_deleted:
                    state_transition(unit, BUILD_STATES.DELETED)
                    if is_misfit:
                        ds_client.delete(unit)
        elif self.build_type == WORKOUT_TYPES.WORKOUT:
            workout = ds_client.get(ds_client.key('cybergym-workout', self.build_id))
            if workout:
                state_transition(workout, BUILD_STATES.DELETED)
                is_misfit = workout.get('misfit', None)
                if is_misfit:
                    ds_client.delete(workout.key)
