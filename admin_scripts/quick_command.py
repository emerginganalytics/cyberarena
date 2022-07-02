import os
import yaml

from utilities.infrastructure_as_code.build_spec_to_cloud import BuildSpecToCloud


cln_yaml = os.path.join("..", "build-files", "workout-specs", "needs-encrypted", "static-arenas", "cln_stoc.yaml")
with open(cln_yaml) as f:
    fixed_arena = yaml.safe_load(f)
spec = BuildSpecToCloud(cyber_arena_spec=fixed_arena)
