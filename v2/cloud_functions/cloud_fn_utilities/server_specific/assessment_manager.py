"""
TODO: Linux_harden_2.py is in good shape. Need to create a template. Also, this class needs to coordinate with the
    schema for the escape_room assessment.
Provides the startup scripts for each server based on the assessment questions in the build.

This module contains the following classes:
    - AssessmentManager: Supplies the build specification for dynamic assessment.
"""

from cloud_fn_utilities.globals import BuildConstants, DatastoreKeyTypes, Buckets
from cloud_fn_utilities.gcp.datastore_manager import DataStoreManager
from cloud_fn_utilities.gcp.cloud_logger import Logger
from cloud_fn_utilities.gcp.cloud_env import CloudEnv

__author__ = "Philip Huff"
__copyright__ = "Copyright 2023, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class AssessmentManager:
    def __init__(self, build_id, key_type=DatastoreKeyTypes.WORKOUT, env_dict=None):
        """

        Args:
            build_id (str): The build ID to query for and use for assessment.
            key_type (str): Indicates the key store
        """
        self.build_id = build_id
        self.key_type = key_type
        self.logger = Logger("cloud_functions.assessment-manager").logger
        self.env = CloudEnv(env_dict=env_dict) if env_dict else CloudEnv()
        self.script_repository = f"gs://{self.env.project}_{Buckets.BUILD_SPEC_BUCKET_SUFFIX}" \
                                 f"/{Buckets.Folders.STARTUP_SCRIPTS.value}"
        self.ds = DataStoreManager(key_type=self.key_type, key_id=self.build_id)
        self.build = self.ds.get()
        if not self.build:
            raise LookupError(f"The datastore record for {self.build_id} no longer exists!")
        if escape_room := self.build.get('escape_room', None):
            self.assessment_questions = escape_room['puzzles']
            self.url = f"{self.env.main_app_url_v2}/api/escape-room/team/"
        else:
            if 'assessment' in self.build and 'questions' in self.build['assessment']:
                self.assessment_questions = self.build['assessment']['questions']
            else:
                self.assessment_questions = None
            self.url = f"{self.env.main_app_url_v2}/api/unit/workout/"


        self.assessment_script = None
        if 'assessment_script' in self.build:
            self.assessment_script = self._create_startup_script(self.build['assessment_script'])

    def get_startup_scripts(self, server_name: str):
        """
        If this is the server running the assessment script, send it the script to include in meta data.

        Args:
            server_name (str): The name of the server to use for adding the script meta data.

        Returns: The startup script to include as meta-data
        """
        if self.assessment_script and self.assessment_questions['server'] == server_name:
            self.logger.info(f"AssessmentManager: Adding the following script to {server_name}: "
                             f"{self.assessment_script}")
            return self.assessment_script
        else:
            return None

    def _create_startup_script(self, assessment_script_spec: dict):
        """
        Creates the initial assessment script structure that will be built with additional question_key environment
        variables. The task string is also created at this point, and will be appended at the end of the script.
        """
        script_operating_system = assessment_script_spec['operating_system']
        script_params = {
            'SCRIPT_REPOSITORY': self.script_repository,
            'SCRIPT': assessment_script_spec['script'],
            'SCRIPT_NAME': f"cyber-arena-assessment",
        }
        # Create operating system specific script pieces.
        if script_operating_system == BuildConstants.ScriptOperatingSystems.WINDOWS:
            key = 'windows-startup-script-bat'
            initial_script = StartupScripts.Windows.env.format(BUILD_ID=self.build_id, URL=self.url)
            if assessment_script_spec['script_language'] == 'python':
                script_params['REOCCURRING_SCRIPT'] = f"python {assessment_script_spec['script']}"
            elif assessment_script_spec['script_language'] == 'powershell':
                script_params['REOCCURRING_SCRIPT'] = f"\"powershell.exe -File ./{assessment_script_spec['script']}\""
            else:
                script_params['REOCCURRING_SCRIPT'] = assessment_script_spec['script']
            task = StartupScripts.Windows.task.format_map(script_params)
        else:
            key = 'startup-script'
            initial_script = StartupScripts.Linux.env.format(BUILD_ID=self.build_id, URL=self.url)
            if assessment_script_spec['script_language'] == 'python':
                script_params['REOCCURRING_SCRIPT'] = f"python3 /usr/bin/{assessment_script_spec['script']}"
            else:
                script_params['REOCCURRING_SCRIPT'] = f"/usr/bin/{assessment_script_spec['script']}"
            task = StartupScripts.Linux.task.format_map(script_params)
        assessment_script = {'key': key, 'value': initial_script}

        # Now add the question-level environment variables.
        for i, question in enumerate(self.assessment_questions):
            if 'script_assessment' in question and question['script_assessment']:
                question_key = question['name']
                if script_operating_system == BuildConstants.ScriptOperatingSystems.WINDOWS:
                    assessment_script['value'] += StartupScripts.Windows.question \
                        .format(NUMBER=i, QUESTION_KEY=question_key)
                else:
                    assessment_script['value'] += StartupScripts.Linux.question \
                        .format(NUMBER=i, QUESTION_KEY=question_key)
        # Finally, add the reoccurring task at the end of the script.
        assessment_script['value'] += task
        return assessment_script


class StartupScripts:
    """
    The Startup Scripts are either Windows or Linux based. Windows runs individual command prompt commands, but
    Linux has a single script file and builds the script file through concatenation.
    """
    class Windows:
        env = 'setx /m BUILD_ID {BUILD_ID}\n' \
              'setx /m URL {URL}\n'
        question = 'setx /m Q_{NUMBER}_KEY {QUESTION_KEY}\n'
        task = 'call gsutil cp {SCRIPT_REPOSITORY}{SCRIPT} .\n' \
               'schtasks /Create /SC MINUTE /TN {SCRIPT_NAME} /RU System /TR {REOCCURRING_SCRIPT}'

    class Linux:
        env = '#! /bin/bash\n' \
              'cat >> /etc/environment << EOF\n' \
              'BUILD_ID={BUILD_ID}\n' \
              'URL={URL}\n'
        question = 'Q_{NUMBER}_KEY={QUESTION_KEY}\n'
        task = 'EOF\n' \
               'gsutil cp {SCRIPT_REPOSITORY}{SCRIPT} /usr/bin\n' \
               '(crontab -l 2>/dev/null; echo "* * * * * {REOCCURRING_SCRIPT}") | crontab -'
