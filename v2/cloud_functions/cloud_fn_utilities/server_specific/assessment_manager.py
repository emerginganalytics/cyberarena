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
    def __init__(self, build_id, env_dict=None):
        """

        Args:
            build_id (str): The build ID to query for and use for assessment.
        """
        self.build_id = build_id
        self.logger = Logger("cloud_functions.assessment-manager").logger
        self.env = CloudEnv(env_dict=env_dict) if env_dict else CloudEnv()
        self.script_repository = f"gs://{self.env.project}_{Buckets.BUILD_SPEC_BUCKET_SUFFIX}" \
                                 f"/{Buckets.Folders.STARTUP_SCRIPTS.value}"
        workout = DataStoreManager(key_type=DatastoreKeyTypes.WORKOUT, key_id=self.build_id).get()
        self.build = DataStoreManager(key_type=DatastoreKeyTypes.UNIT, key_id=workout['parent_id']).get()
        if not self.build:
            raise LookupError(f"The datastore record for {self.build_id} no longer exists!")
        self.url = self._get_url()
        self.assessment_questions = self._get_assessment_questions()
        self.assessment_script_spec = self._get_assessment_script_spec()

    def get_startup_scripts(self, server_name: str):
        """
        If this is the server running the assessment script, send it the script to include in meta data.

        Args:
            server_name (str): The name of the server to use for adding the script meta data.

        Returns: The startup script to include as meta-data
        """
        if self.assessment_script_spec and self.assessment_script_spec['server'] == server_name:
            self.logger.info(f"AssessmentManager: Adding the following script to {server_name}: "
                             f"{self.assessment_script_spec}")
            return self._create_startup_script()
        else:
            return None

    def _get_url(self):
        path = '/api/escape-room/team/' if 'escape_room' in self.build else '/api/unit/workout/'
        return f"{self.env.main_app_url_v2}{path}"

    def _get_assessment_questions(self):
        if escape_room := self.build.get('escape_room', None):
            return escape_room['puzzles']
        else:
            if 'assessment' in self.build and 'questions' in self.build['assessment']:
                return self.build['assessment']['questions']
            elif 'lms_quiz' in self.build and 'questions' in self.build['lms_quiz']:
                return self.build['lms_quiz']['questions']
            else:
                return None

    def _get_assessment_script_spec(self):
        if 'lms_quiz' in self.build and 'assessment_script' in self.build['lms_quiz']:
            return self.build['lms_quiz']['assessment_script']
        elif 'assessment' in self.build and 'assessment_script' in self.build['assessment']:
            return self.build['assessment']['assessment_script']
        else:
            return None

    def _create_startup_script(self):
        """
        Creates the initial assessment script structure that will be built with additional question_key environment
        variables. The task string is also created at this point, and will be appended at the end of the script.
        """
        script_operating_system = self.assessment_script_spec['operating_system']
        script_params = {
            'SCRIPT_REPOSITORY': self.script_repository,
            'SCRIPT': self.assessment_script_spec['script'],
            'SCRIPT_NAME': f"cyber-arena-assessment",
        }
        # Create operating system specific script pieces.
        if script_operating_system == BuildConstants.ScriptOperatingSystems.WINDOWS:
            key = 'windows-startup-script-bat'
            initial_script = StartupScripts.Windows.env.format(BUILD_ID=self.build_id, URL=self.url)
            if self.assessment_script_spec['script_language'] == 'python':
                script_params['REOCCURRING_SCRIPT'] = f"python {self.assessment_script_spec['script']}"
            elif self.assessment_script_spec['script_language'] == 'powershell':
                script_params['REOCCURRING_SCRIPT'] = f"\"powershell.exe -File ./" \
                                                      f"{self.assessment_script_spec['script']}\""
            else:
                script_params['REOCCURRING_SCRIPT'] = self.assessment_script_spec['script']
            task = StartupScripts.Windows.task.format_map(script_params)
        else:
            key = 'startup-script'
            initial_script = StartupScripts.Linux.env.format(BUILD_ID=self.build_id, URL=self.url)
            if self.assessment_script_spec['script_language'] == 'python':
                script_params['REOCCURRING_SCRIPT'] = f"python3 /usr/bin/{self.assessment_script_spec['script']}"
            else:
                script_params['REOCCURRING_SCRIPT'] = f"/usr/bin/{self.assessment_script_spec['script']}"
            task = StartupScripts.Linux.task.format_map(script_params)
        assessment_script = {'key': key, 'value': initial_script}
        # Add the question environment variables
        assessment_script['value'] = self._add_question_env(assessment_script['value'], script_operating_system)
        # Finally, add the reoccurring task at the end of the script.
        assessment_script['value'] += task
        return assessment_script

    def _add_question_env(self, assessment_script, script_operating_system):
        for i, question in enumerate(self.assessment_questions):
            if 'script_assessment' in question and question['script_assessment']:
                question_key = question['question_key']
                if script_operating_system == BuildConstants.ScriptOperatingSystems.WINDOWS:
                    assessment_script += StartupScripts.Windows.question.format(NUMBER=i, QUESTION_KEY=question_key)
                else:
                    assessment_script += StartupScripts.Linux.question.format(NUMBER=i, QUESTION_KEY=question_key)
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
