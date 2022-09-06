from marshmallow import Schema, fields, validate
from main_app_utilities.globals import BuildConstants


class AttackSchema(Schema):
    id = fields.Str(required=True)
    version = fields.Str(required=True)
    description = fields.Str(required=True)
    attack_name = fields.Str(required=True)
    attack_type = fields.Str(required=True)
    mitre_attack = fields.Str(required=True)
    mode = fields.Str(required=True)
    args = fields.Nested('ArgSchema', many=True, required=True)
    creation_timestamp = fields.Float()
    expires = fields.Float(required=True)


class ArgSchema(Schema):
    id = fields.Str(required=True)
    type = fields.Str(required=True)
    hint = fields.Str(required=True)
    name = fields.Str(required=True)
    network = fields.Nested('NetworkSchema', required=True)
    choices = fields.Nested('ArgChoiceSchema', many=True, required=False)


class ArgChoiceSchema(Schema):
    choice = fields.Str(required=True)


class NetworkSchema(Schema):
    id = fields.Str(required=True)
    name = fields.Str(required=True)
    ip = fields.Str(required=True)

