from cloud_fn_utilities.globals import DatastoreKeyTypes, get_current_timestamp_utc, BuildConstants
from cloud_fn_utilities.gcp.datastore_manager import DataStoreManager
from cloud_fn_utilities.lms.lms_synchronizer import LMSSynchronizer
from cloud_fn_utilities.lms.canvas.lms_canvas import LMSCanvas


__author__ = "Philip Huff"
__copyright__ = "Copyright 2023, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff"]
__license__ = "MIT"
__version__ = "0.1.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Production"


class LMSCanvasSynchronizer(LMSSynchronizer):
    def __init__(self, env_dict=None):
        super().__init__(env_dict=env_dict)

    def _get_active_lms_units(self):
        ds = DataStoreManager(key_type=DatastoreKeyTypes.UNIT)
        active_units = ds.query(filters=[('workspace_settings.expires', '<', get_current_timestamp_utc())])
        active_lms_units = []
        for unit in active_units:
            if 'lms_connection' in unit and unit['lms_connection']['lms_type'] == BuildConstants.LMS.CANVAS:
                active_lms_units.append(unit)
        return active_lms_units

    def _get_active_students(self, unit):
        url = unit['lms_connection']['url']
        api_key = unit['lms_connection']['api_key']
        course_code = unit['lms_connection']['course_code']
        course_key = f"{url}-{course_code}"
        # This cache speeds up the function in cases where courses have several quizzes
        if course_key not in self.student_list_cache:
            lms = LMSCanvas(url=url, api_key=api_key, course_code=course_code, build=unit)
            class_list = lms.get_class_list(suppress_logs=True)
            self.student_list_cache[course_key] = class_list
        else:
            class_list = self.student_list_cache[course_key]
        return class_list
