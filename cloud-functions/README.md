The following cloud functions must be installed along with the topics and scheduler. These functions are containers for managing the lifecycle of any given workout.

<table data-layout="default"><colgroup><col style="width: 154.0px;"><col style="width: 259.0px;"><col style="width: 346.0px;"></colgroup>

<tbody>

<tr>

<th>

**Function**

</th>

<th>

**Description**

</th>

<th>

**Schedule**

</th>

</tr>

<tr>

<td>

function-build-workouts

</td>

<td>

Builds a single workout according to a specification and sets the correct datastore flag when complete.

</td>

<td>

**On-demand** from the main application. Triggers pub/sub topic _build-workouts_

</td>

</tr>

<tr>

<td>

function-start-workout

</td>

<td>

Starts all workout resources. This is to offload long-running tasks from the web application.

</td>

<td>

**On-demand** from the main application. Triggers pub/sub topic _start-workout_

</td>

</tr>

<tr>

<td>

function-stop-start-workout

</td>

<td>

Stops and starts all workout resources. This is to offload long-running tasks from the web application

</td>

<td>

**On-demand** from the main application. Triggers pub/sub topic _stop-start-workout_

</td>

</tr>

<tr>

<td>

function-delete-expired-workouts

</td>

<td>

Deletes any workout resources (i.e., servers, networks, routes, firewall rules, DNS entries) past its expiration date listed in the datastore.

</td>

<td>

Runs **hourly** through _maint-del-job_ cloud scheduler. Triggers pub/sub topic: _maint-del-systems_

</td>

</tr>

<tr>

<td>

function_stop_workouts

</td>

<td>

Stops any workouts which are running beyond their specified runtime as listed in the datastore.

</td>

<td>

Runs **every 15 minutes** through _stop-workouts_ cloud scheduler. Triggers pub/sub topic: _stop-workouts_

</td>

</tr>

<tr>

<td>

function_wrong_state_checker

</td>

<td>

There are circumstances in which a server may be running when their datastore state is listed as _stopped_. This function will correct the state

</td>

<td>

Runs **daily** through _wrong_state_checker_ cloud scheduler. Triggers pub/sub topic: _wrong_state_checker_

</td>

</tr>

<tr>

<td>

function-build-arena

</td>

<td>

Build an arena of multiple student servers and multiple central servers

</td>

<td>

**On-demand** from the main application. Triggers pub/sub topic _build-arena_ with unit_id passed in the context

</td>

</tr>

<tr>

<td>

function-stop-arenas

</td>

<td>

Stops any arenas running beyond their specified run time

</td>

<td>

Runs **every 15 minutes** through _job-stop-lapsed-arenas_ cloud scheduler. Triggers pub/sub topic: _stop-lapsed-arenas_

</td>

</tr>

<tr>

<td>

function-delete-expired-workouts

</td>

<td>

Delete any expired or misfit arena resources

</td>

<td>

Runs **hourly** through _job-delete-expired-arena_ cloud scheduler. Triggers pub/sub topic: _delete-arena_

</td>

</tr>

<tr>

<td>

function-stop-all-workouts

</td>

<td>

Stops all running workouts

</td>

<td>

Runs **daily** at midnight through _job-stop-all-servers_ cloud scheduler. Triggers pub/sub topic: _stop-all-servers_

</td>

</tr>

<tr>

<td>

function-start-arena

</td>

<td>

Starts arena servers

</td>

<td>

**On-demand** from the main application. Triggers pub/sub topic _start-arena_ with unit_id passed in the context

</td>

</tr>

</tbody>

</table>