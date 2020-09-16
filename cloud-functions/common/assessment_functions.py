from pathlib import Path

from common.globals import workout_globals

def get_startup_scripts(workout_id, assessment):
    """
    Parses the assessment specification to obtain any startup script metadata on the specified server.
    Returns the startup script data for common.build_workout to include in the specified server startup script
    metadata.
    :param workout_id: The ID of the workout assessment being parsed
    :param assessment: A dictionary structured according to the assessment specification in the yaml where
    each question may have an auto assessment script which needs to run.
    :return: An array of dictionaries specifying the server and startup script or none if there are no startup
    scripts. The structure of a startup script
    {
        'servername': {'key': 'windows-startup-script-bat', 'value': <the specified startup script>,
    }
    """
    startup_scripts = {}
    i = 0

    for question in assessment['questions']:
        if question['type'] == 'auto':
            if question['operating-system'] == 'windows':
                if question['server'] not in startup_scripts:
                    script = workout_globals.windows_startup_script_env.format(env_workoutid=workout_id)
                    startup_scripts[question['server']] = {
                            'key': 'windows-startup-script-bat',
                            'value': script
                        }
                if 'script_language' in question and question['script_language'] == 'python':
                    script_command = 'python {script}'.format(script=question['script'])
                elif 'script_language' in question and question['script_language'] == 'powershell':
                    script_command = 'powershell.exe -File ./{script}'.format(script=question['script'])
                    script_command = f'"{script_command}"'
                else:
                    script_command = question['script']
                assess_script = workout_globals.windows_startup_script_task.format(env_workoutkey=question['key'],
                                                                                   q_number=i,
                                                                                   script_name='Assess' + str(i),
                                                                                   script=question['script'],
                                                                                   script_command=script_command)

            else:
                if question['server'] not in startup_scripts:
                    script = workout_globals.linux_startup_script_env.format(env_workoutid=workout_id)
                    startup_scripts[question['server']] = {
                            'key': 'startup-script',
                            'value': script
                        }
                if 'script_language' in question and question['script_language'] == 'python':
                    script = 'python3 {script}'.format(script=question['script'])
                else:
                    script = question['script']
                assess_script = workout_globals.linux_startup_script_task.format(env_workoutkey=question['key'],
                                                                                   q_number=i,
                                                                                   script=script)
            if i != 0:
                startup_scripts[question['server']]['value'] += "\n"
            startup_scripts[question['server']]['value'] += assess_script
            i += 1

    if len(startup_scripts) == 0:
        startup_scripts = None
    return startup_scripts
