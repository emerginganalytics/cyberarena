from marshmallow import Schema, fields, validate


class AttackSchema(Schema):
    id = fields.Str(required=True)
    args = fields.Nested('ArgSchema', many=True, required=True)
    attack_name = fields.Str(required=True)
    attack_type = fields.Str(required=True)
    mitre_attack = fields.Str(required=True)
    mode = fields.Str(required=True)
    description = fields.Str(required=True)


class ArgSchema(Schema):
    id = fields.Str(required=True)
    type = fields.Str(required=True)
    hint = fields.Str(required=True)
    name = fields.Str(required=True)
    choices = fields.Nested('ArgChoiceSchema', many=True)


class ArgChoiceSchema(Schema):
    choice = fields.Str(required=True)
