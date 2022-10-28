import os
import yaml

from utilities.infrastructure_as_code.build_spec_to_cloud import BuildSpecToCloud
from common.build_workout import build_workout
from common.start_vm import start_vm
from common.delete_expired_workouts import DeletionManager

DeletionManager(deletion_type=DeletionManager.DeletionType.EXPIRED)
