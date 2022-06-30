import time
from datetime import datetime
from google.cloud import datastore


from install.utilities.globals import InstallUpdateTypes
from install.stages.stage1_base_build import BaseBuild
from install.stages.stage2_environment_variables import EnvironmentVariables

__author__ = "Philip Huff"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class InstallUpdateManager:
    CURRENT_VERSION = 2.0

    def __init__(self, selection, project):
        self.selection = selection
        self.project = project
        self._create_update_record()

    def run(self):
        if self.selection == InstallUpdateTypes.FULL:
            BaseBuild(project=self.project).run()
            EnvironmentVariables(project=self.project).run()

    def _create_update_record(self):
        update_time = time.time()
        update_info = {
            'version': self.CURRENT_VERSION,
            'action': self.selection,
            'update_time': datetime.utcnow().isoformat(),
        }

        ds_client = datastore.Client()
        ds_entity = datastore.Entity(ds_client.key('cyberarena-updates', update_time))
        ds_entity.update(update_info)
        ds_client.put(ds_entity)
