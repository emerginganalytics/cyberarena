from cloud_fn_utilities.globals import DatastoreKeyTypes
from cloud_fn_utilities.gcp.cloud_env import CloudEnv
from cloud_fn_utilities.gcp.datastore_manager import DataStoreManager
from cloud_fn_utilities.cyber_arena_objects.unit import Unit


__author__ = "Philip Huff"
__copyright__ = "Copyright 2023, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff"]
__license__ = "MIT"
__version__ = "0.1.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Production"


class LMSSynchronizer:
    def __init__(self, env_dict=None):
        self.env = CloudEnv(env_dict=env_dict) if env_dict else CloudEnv()
        self.env_dict = self.env.get_env()
        self.student_list_cache = {}

    def sync_units_with_class_list(self):
        # Identify each unit with lms build
        units = self._get_active_lms_units()
        for unit in units:
            unit_id = unit['id']
            ds_unit = DataStoreManager(key_type=DatastoreKeyTypes.UNIT, key_id=unit_id)
            unit_obj = Unit(build_id=unit_id, env_dict=self.env_dict)
            active_students = self._get_active_students(unit=unit)
            new_student_emails = [student['email'] for student in active_students]
            workouts = ds_unit.get_children(child_key_type=DatastoreKeyTypes.WORKOUT, parent_id=unit_id, wait=False)
            for workout in workouts:
                student_email = workout.get('student_email', '').lower()
                if student_email in new_student_emails:
                    new_student_emails.remove(student_email)
            for student in active_students:
                if student['email'] in new_student_emails:
                    unit_obj.add_student_workout_record(student_email=student['email'], student_name=student['name'])

    def _get_active_lms_units(self):
        raise NotImplementedError("_get_active_lms_units not implemented for this object.")

    def _get_active_students(self, unit):
        raise NotImplementedError("_get_active_students not implemented for this object.")
