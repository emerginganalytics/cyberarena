"""
Provides the startup scripts for each server based on the assessment questions in the build.

This module contains the following classes:
    - AssessmentManager: Supplies the build specification for dynamic assessment.
"""

import json
from cloud_fn_utilities.globals import BuildConstants, DatastoreKeyTypes, Buckets
from cloud_fn_utilities.gcp.datastore_manager import DataStoreManager
from cloud_fn_utilities.gcp.cloud_logger import Logger
from cloud_fn_utilities.gcp.cloud_env import CloudEnv
import time

__author__ = "Philip Huff"
__copyright__ = "Copyright 2023, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class AssessmentManager:
    def __init__(self, build_id, key_type=DatastoreKeyTypes.WORKOUT):
        """

        Args:
            build_id (str): The build ID to query for and use for assessment.
            key_type (str): Indicates the key store
        """
        self.build_id = build_id
        self.key_type = key_type
        self.logger = Logger("cloud_functions.assessment-manager").logger
        self.env = CloudEnv()
        self.script_repository = f"gs://{self.env.project}_{Buckets.BUILD_SPEC_BUCKET_SUFFIX}" \
                                 f"/{Buckets.Folders.STARTUP_SCRIPTS.value}"
        self.ds = DataStoreManager(key_type=self.key_type, key_id=self.build_id)
        self.build = self.ds.get()
        if not self.build:
            raise LookupError(f"The datastore record for {self.build_id} no longer exists!")
        if 'build_type' in self.build:
            self.build_type = self.build['build_type']
            if self.build_type == BuildConstants.BuildType.ESCAPE_ROOM:
                self.assessment_questions = self.build['escape_room']['puzzles']
                self.url = f"https://{self.env.main_app_url}/api/escape-room/team/"
            else:
                self.assessment_questions = self.build.get('assessment', None)
                # TODO: Add a URL for the workout assessment.
        else:
            raise ValueError(f"The build object for the assessment has no build_type key")

    def get_startup_scripts(self, server_name: str):
        """
        Parses through the unit and returns any startup scripts needed for auto assessment.

        Args:
            server_name (str): The name of the server to use for adding the script meta data.

        Returns: The startup script to include as meta-data

        """
        startup_script = None
        i = 0
        for question in self.assessment_questions:
            if question['type'] == BuildConstants.QuestionTypes.AUTO and 'server' in question \
                    and question['server'] == server_name:
                if question['operating_system'] == BuildConstants.ScriptOperatingSystems.WINDOWS:
                    script = StartupScripts.windows_startup_script_env.format(
                        BUILD_ID=self.build_id,
                        URL=self.url
                    )
                    startup_script = {
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

                    assess_script = StartupScripts.windows_startup_script_task.format(
                        QUESTION_KEY=question['id'],
                        Q_NUMBER=i,
                        SCRIPT_REPOSITORY=self.script_repository,
                        SCRIPT=question['script'],
                        SCRIPT_NAME='Assess' + str(i),
                        SCRIPT_COMMAND=script_command)
                else:
                    script = StartupScripts.linux_startup_script_env.format(BUILD_ID=self.build_id, URL=self.url)
                    startup_script = {
                        'key': 'startup-script',
                        'value': script
                    }
                    if 'script_language' in question and question['script_language'] == 'python':
                        script_command = f"python3 /usr/bin/{question['script']}"
                    else:
                        script_command = f"/usr/bin/{question['script']}"
                    assess_script = StartupScripts.linux_startup_script_task.format(
                        QUESTION_KEY=question['id'],
                        Q_NUMBER=i,
                        SCRIPT_REPOSITORY=self.script_repository,
                        SCRIPT=question['script'],
                        LOCAL_STORAGE="/usr/bin",
                        SCRIPT_COMMAND=script_command)
                if i != 0:
                    startup_script['value'] += "\n"
                startup_script['value'] += assess_script
                i += 1

        return startup_script


class StartupScripts:
    windows_startup_script_env = 'setx /m BUILD_ID {BUILD_ID}\n' \
                                 'setx /m URL {URL}\n'
    windows_startup_script_task = 'setx /m Q{Q_NUMBER}_KEY {QUESTION_KEY}\n' \
                                  'call gsutil cp {SCRIPT_REPOSITORY}{SCRIPT} .\n' \
                                  'schtasks /Create /SC MINUTE /TN {SCRIPT_NAME} /RU System /TR {SCRIPT_COMMAND}'
    linux_startup_script_env = '#! /bin/bash\n' \
                               'cat >> /etc/environment << EOF\n' \
                               'BUILD_ID={BUILD_ID}\n' \
                               'URL={URL}\n'
    linux_startup_script_task = 'cat >> /etc/environment << EOF\n' \
                                'Q{Q_NUMBER}={QUESTION_KEY}\n' \
                                'EOF\n' \
                                'gsutil cp {SCRIPT_REPOSITORY}{SCRIPT} {LOCAL_STORAGE}\n'\
                                '(crontab -l 2>/dev/null; echo "* * * * * {SCRIPT_COMMAND}") | crontab -'
