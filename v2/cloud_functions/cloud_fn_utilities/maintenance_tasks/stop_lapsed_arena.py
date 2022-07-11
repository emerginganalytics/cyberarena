import time, calendar

import schedule
from google.cloud import pubsub_v1
from self import self

from common.globals import ds_client, log_client, project, compute, BUILD_STATES, PUBSUB_TOPICS, SERVER_ACTIONS, LOG_LEVELS
from common.state_transition import state_transition
import time, calendar
from google.cloud import pubsub_v1
from common.globals import ds_client, log_client, project, compute, BUILD_STATES, PUBSUB_TOPICS, SERVER_ACTIONS, LOG_LEVELS
from common.state_transition import state_transition
from common.stop_compute import stop_workout

class StopLapsedArena():

  def stop_lapsed_workouts(self):
    # Get the current time to compare with the start time to see if a workout needs to stop
    ts = calendar.timegm(time.gmtime())

    # Query all workouts which have not been deleted
    query_workouts = ds_client.query(kind='cybergym-workout')
    query_workouts.add_filter("state", "=", BUILD_STATES.RUNNING)
    for workout in list(query_workouts.fetch()):
        workout_project = workout.get('build_project_location', project)
        if workout_project == project:
            if "start_time" in workout and "run_hours" in workout and workout.get('type', 'arena') != 'arena':
                workout_id = workout.key.name
                start_time = int(workout.get('start_time', 0))
                run_hours = int(workout.get('run_hours', 0))

                # Stop the workout servers if the run time has exceeded the request
                if ts - start_time >= run_hours * 3600:
                    g_logger = log_client.logger(str(workout_id))
                    g_logger.log_struct(
                        {
                            "message": "The workout {} has exceeded its run time and will be stopped".format(workout_id)
                        }, severity=LOG_LEVELS.INFO
                    )

                    stop_workout(workout_id)

  schedule.every(15).minute.do(stop_lapsed_workouts, self)
