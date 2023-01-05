from marshmallow import Schema, fields
from main_app_utilities.globals import BuildConstants


class AttackSchema(Schema):
    id = fields.Str(required=True)
    name = fields.Str(required=True, help_text='Name of the attack specification')
    module = fields.Str(required=True, help_text='Name of the script to run on the machine')
    mitre_attack = fields.Str(required=True, help_text='Mappings to MITRE Att&ck Framework')
    description = fields.Str(required=True)
    attack_type = fields.Str(required=True, help_text="Describes attack method, i.e. scanning, exploitation, etc.")
    mode = fields.Str(required=True, help_text="Either type attack or type weakness")
    args = fields.Nested('ArgSchema', required=True, help_text="User selected options to help build attack script")
    creation_timestamp = fields.DateTime()
    parent_id = fields.Str(required=True)
    parent_build_type = fields.Str(required=True, default=BuildConstants.BuildType.FIXED_ARENA_CLASS.value)


class ArgSchema(Schema):
    target_id = fields.Str(required=True,
                           help_text="Identifier of Cyber Arena build the "
                                     "attack will be sent to, e.g. classroom or workspace id")
    target_build_type = fields.Str(required=True, default=BuildConstants.BuildType.FIXED_ARENA_CLASS.value,
                                   help_text="Defines what build_type target is.")
    target_machine = fields.Str(required=True, help_text="Name of server to direct attack towards.")
    option = fields.Str(required=False, help_text="Optional arguments to change the attack script function.")


class ArgOptionSchema(Schema):
    option = fields.Str(required=True)


class TargetSchema(Schema):
    id = fields.Str(required=True)
