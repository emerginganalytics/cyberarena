import time
import calendar
from google.cloud import datastore
from google.cloud import pubsub_v1
from utilities.globals import ds_client, storage_client, workout_globals, project, dns_suffix, log_client, LOG_LEVELS, \
    BUILD_STATES, cloud_log, AdminInfoEntity, LogIDs, BuildTypes


class ChildProjectManager:
    """
    Performs a workout build across multiple parent and child projects. This allows builds to expand beyond
    the limited project quotas.
    Usage:
        pm = ChildProjectManager(unit_id)
        workouts_built = pm.build_workouts()
    """
    MAX_BUILDS = 300

    def __init__(self, unit_id):
        self.allocation = {}
        self.unit_id = unit_id
        unit_workouts = ds_client.query(kind='cybergym-workout')
        unit_workouts.add_filter("unit_id", "=", unit_id)
        self.workouts = list(unit_workouts.fetch())
        self.workout_count = len(self.workouts)
        self.remaining_count = self.workout_count

    def build_workouts(self):
        """
        Build workouts according to the available allocations.
        @return: Boolean on whether this successfully built
        @rtype:
        """
        self._get_build_allocation()
        if not self.allocation:
            # If there are not enough resource, delete the unit from the datastore before returning.
            for workout in self.workouts:
                ds_client.delete(workout.key)
            return False
        _projects = list(self.allocation.keys())
        i = 0
        j = 0
        publisher = topic_path = current_project = None
        for workout in self.workouts:
            if i == 0:
                current_project = _projects[j]
                j += 1

                publisher = pubsub_v1.PublisherClient()
                topic_path = publisher.topic_path(current_project, workout_globals.ps_build_workout_topic)
            workout['build_project_location'] = current_project
            ds_client.put(workout)
            publisher.publish(topic_path, data=b'Cyber Gym Workout', workout_id=workout.key.name)

            i += 1
            # If the index is greater than the current project's build allocation, reset the index, which triggers
            # a project change on the next iteration.
            if i >= self.allocation[current_project]:
                i = 0
        return True


    def _get_build_allocation(self):
        """
        Identify the build allocation among the parent and all children based on available resources and identified
        quotas.
        @param workout_count: Number of workouts to build in this request
        @type workout_count: Integer
        @return: The parent/or children projects to use, which may split across multiple projects
        @rtype: Dict {'<parent>': 80, '<child1>': 300, '<child2>': 300}
        """
        # First, get all available projects.
        available = {project: self.MAX_BUILDS}
        admin_info = ds_client.get(ds_client.key(AdminInfoEntity.KIND, 'cybergym'))
        if AdminInfoEntity.Entities.CHILD_PROJECTS in admin_info:
            for child_project in admin_info[AdminInfoEntity.Entities.CHILD_PROJECTS]:
                available[child_project] = self.MAX_BUILDS

        # Next find all active workouts for the application
        query_workouts = ds_client.query(kind='cybergym-workout')
        query_workouts.add_filter('active', '=', True)

        # Determine the available build left for each parent and children projects.
        for workout in list(query_workouts.fetch()):
            workout_project = workout.get('build_project_location', project)
            if workout_project not in available:
                cloud_log(LogIDs.MAIN_APP, f"Error in workout specification. The project {workout_project} is not "
                                           f"a valid project for this application.", LOG_LEVELS.ERROR)
                return False
            available[workout_project] -= 1

        # Set the build allocation for this project based on availability.
        for _project in available:
            workouts_available = available[_project]
            if workouts_available > 0:
                _project_allocation = min(self.remaining_count, workouts_available)
                self.allocation[_project] = _project_allocation
                self.remaining_count -= _project_allocation

        if self.remaining_count > 0:
            cloud_log(LogIDs.MAIN_APP, "Error: Not enough available resources to complete the build!", LOG_LEVELS.ERROR)
            return False
        else:
            return True
