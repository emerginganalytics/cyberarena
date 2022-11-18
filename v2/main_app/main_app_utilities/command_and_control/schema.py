from marshmallow import Schema, fields
from main_app_utilities.globals import BuildConstants


class AttackSchema(Schema):
    id = fields.Str(required=True)
    name = fields.Str(required=True)
    module = fields.Str(required=True)
    mitre_attack = fields.Str(required=True)
    description = fields.Str(required=True)
    attack_type = fields.Str(required=True)
    mode = fields.Str(required=True)
    args = fields.Nested('ArgSchema', required=True)
    creation_timestamp = fields.Float()
    parent_id = fields.Str(required=True)
    parent_build_type = fields.Str(required=True, default=BuildConstants.BuildType.FIXED_ARENA_CLASS.value)


class ArgSchema(Schema):
    target_id = fields.Str(required=True)
    target_build_type = fields.Str(required=True, default=BuildConstants.BuildType.FIXED_ARENA_CLASS.value)
    target_machine = fields.Str(required=True)
    option = fields.Str(required=True)


class ArgOptionSchema(Schema):
    option = fields.Str(required=True)


class NetworkSchema(Schema):
    id = fields.Str(required=True)
