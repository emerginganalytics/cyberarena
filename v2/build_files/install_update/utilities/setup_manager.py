import time
from datetime import datetime
from google.cloud import datastore


from install_update.utilities.globals import SetupOptions
from install_update.operations.base_build import BaseBuild
from install_update.operations.environment_variables import EnvironmentVariables
from install_update.operations.cyber_arena_app import CyberArenaApp
from install_update.operations.build_specification import BuildSpecification
from install_update.operations.bulk_install_update import BulkInstallUpdate
from install_update.operations.cloud_database import CloudDatabase

__author__ = "Philip Huff"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class SetupManager:
    CURRENT_VERSION = 2.0

    def __init__(self, selection, project):
        self.selection = selection
        self.project = project

    def run(self):
        if self.selection == SetupOptions.FULL:
            BaseBuild(project=self.project).run()
            cyber_arena_app = CyberArenaApp()
            app_deployed = cyber_arena_app.deploy_main_app()
            function_deployed = cyber_arena_app.deploy_cloud_functions()
            if app_deployed and function_deployed:
                self._create_update_record()
        elif self.selection == SetupOptions.UPDATE:
            cyber_arena_app = CyberArenaApp()
            app_deployed = cyber_arena_app.deploy_main_app()
            function_deployed = cyber_arena_app.deploy_cloud_functions()
            if app_deployed and function_deployed:
                self._create_update_record()
        elif self.selection == SetupOptions.CLOUD_FUNCTION:
            CyberArenaApp().deploy_cloud_functions()
        elif self.selection == SetupOptions.MAIN_APP:
            CyberArenaApp().deploy_main_app()
        elif self.selection == SetupOptions.BUILD_SPECS:
            BuildSpecification().run()
        elif self.selection == SetupOptions.PREPARE_SPEC:
            BuildSpecification().sync_single_spec()
        elif self.selection == SetupOptions.DECRYPT_SPECS:
            BuildSpecification(sync=False).decrypt_locked_folders()
        elif self.selection == SetupOptions.ENV:
            EnvironmentVariables(project=self.project).run()
        elif self.selection == SetupOptions.SQL:
            CloudDatabase().deploy()
        elif self.selection == SetupOptions.BULK_UPDATE:
            BulkInstallUpdate().run()
        else:
            return

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
