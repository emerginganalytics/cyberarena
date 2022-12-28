from marshmallow import Schema, fields, validate

from main_app_utilities.globals import BuildConstants

__author__ = "Philip Huff"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class FixedArenaSchema(Schema):
    id = fields.Str(description='unique ID for the fixed arena', required=True)
    creation_timestamp = fields.DateTime()
    version = fields.Str(required=True)
    build_type = fields.Str(required=True, validate=validate.OneOf([x for x in BuildConstants.BuildType]))
    summary = fields.Nested('CyberArenaSummarySchema', required=True)
    networks = fields.Nested('NetworkSchema', many=True, required=True)
    servers = fields.Nested('ServerSchema', many=True, required=True)
    firewalls = fields.Nested('FirewallSchema', many=True)
    firewall_rules = fields.Nested('FirewallRuleSchema', many=True)

    class Meta:
        strict = True


class FixedArenaClassSchema(Schema):
    id = fields.Str(required=True)
    creation_timestamp = fields.Float()
    version = fields.Str(required=True)
    workspace_settings = fields.Nested('WorkspaceSettingsSchema')
    build_type = fields.Str(required=True, validate=validate.OneOf([x for x in BuildConstants.BuildType]))
    parent_id = fields.Str(description='The Fixed Arena ID in which this is built', required=True)
    summary = fields.Nested('CyberArenaSummarySchema', required=True)
    workspace_servers = fields.Nested('ServerSchema', many=True, required=True)
    fixed_arena_servers = fields.List(fields.Str, description='A list of servers to turn on in the fixed arena.',
                                      default=[])
    assessment = fields.Nested('AssessmentSchema', required=False)
    add_attacker = fields.Bool(description="Whether to add an attacker (agent) machine to the workspace networks",
                               default=False)


class UnitSchema(Schema):
    id = fields.Str(required=True)
    creation_timestamp = fields.Float()
    version = fields.Str(required=True)
    class_id = fields.Str(required=False)
    instructor_id = fields.Str(required=True)
    workspace_settings = fields.Nested('WorkspaceSettingsSchema')
    build_type = fields.Str(required=True, validate=validate.OneOf([x for x in BuildConstants.BuildType]))
    summary = fields.Nested('CyberArenaSummarySchema', required=True)
    networks = fields.Nested('NetworkSchema', many=True, required=False)
    servers = fields.Nested('ServerSchema', many=True, required=False)
    web_applications = fields.Nested('WebApplicationSchema', many=True, required=False,
                                     description="Used for cloud container labs")
    firewall_rules = fields.Nested('FirewallRuleSchema', many=True, description="These are ONLY set by the program to "
                                                                                "allow all internal traffic")
    assessment = fields.Nested('AssessmentSchema', required=False)
    escape_room = fields.Nested('EscapeRoomSchema', required=False,
                                description="Escape room units include additional specification of the escape room "
                                            "puzzles associated with each workout")
    test = fields.Bool(required=False, description="Whether the unit is a test. This helps in cleaning the datastore.")


class WorkspaceSettingsSchema(Schema):
    count = fields.Int(description='The number of distinct workstation builds to deploy', required=True)
    registration_required = fields.Bool(description='Whether students must login to access this build', default=False)
    student_emails = fields.List(fields.Str, description='Email addresses of students when registration is required',
                                 many=True, required=False)
    student_names = fields.List(fields.Str, description='Name of the student assigned to the workspaces',
                                many=True, required=False)
    expires = fields.Float(required=True)


class CyberArenaSummarySchema(Schema):
    name = fields.Str(required=True)
    description = fields.Str(required=True)
    teacher_instructions_url = fields.URL(required=False, allow_none=True)
    student_instructions_url = fields.URL(required=False, allow_none=True)
    hourly_cost = fields.Float(required=False, allow_none=True)
    author = fields.Str(required=False, allow_none=True)

    class Meta:
        strict = True


class NetworkSchema(Schema):
    name = fields.Str(required=True)
    subnets = fields.Nested('SubNetworkSchema', many=True)

    class Meta:
        strict = True


class SubNetworkSchema(Schema):
    name = fields.Str(required=True)
    ip_subnet = fields.Str(required=True)
    class Meta:
        strict = True


class ServerSchema(Schema):
    name = fields.Str(required=True)
    image = fields.Str(required=True)
    machine_type = fields.Str(required=True, default="e1-standard1")
    add_disk = fields.Int(required=False, default=0)
    tags = fields.List(fields.Str)
    build_type = fields.Str(default=None)
    metadata = fields.Str(default=None)
    sshkey = fields.Str(default=None)
    can_ip_forward = fields.Bool(default=False)
    alias_ip_addresses = fields.List(fields.Str)
    min_cpu_platform = fields.Str(default="")
    nics = fields.Nested('NicSchema', many=True)
    human_interaction = fields.Nested('HumanInteractionSchema', many=True)

    class Meta:
        strict = True


class NicSchema(Schema):
    network = fields.Str(required=True)
    internal_ip = fields.Str(required=True)
    subnet_name = fields.Str(required=True, default="default")
    external_nat = fields.Bool(default=False)

    class Meta:
        strict = True


class HumanInteractionSchema(Schema):
    display = fields.Bool(default=False)
    protocol = fields.Str(required=True, validate=validate.OneOf([x for x in BuildConstants.Protocols]))
    username = fields.Str()
    password = fields.Str()
    domain = fields.Str()
    security_mode = fields.Str()


class WebApplicationSchema(Schema):
    name = fields.Str(required=True, description="Display name of the container")
    host_name = fields.Str(required=True, description="Host name for the URL")
    starting_directory = fields.Str(required=True, description="The starting web directory for the container URL")


class FirewallSchema(Schema):
    name = fields.Str(required=True)
    type = fields.Str(required=True, validate=validate.OneOf([x for x in BuildConstants.Firewalls]))
    gateway = fields.Str(required=True)
    networks = fields.List(fields.Str(), required=True)

    class Meta:
        strict = True


class FirewallRuleSchema(Schema):
    name = fields.Str(required=True)
    network = fields.Str(required=True)
    target_tags = fields.List(fields.Str())
    protocol = fields.Str(validate=validate.OneOf([x for x in BuildConstants.TransportProtocols]))
    ports = fields.List(fields.Str())
    source_ranges = fields.List(fields.Str, default=["0.0.0.0/0"])

    class Meta:
        strict = True


class AssessmentSchema(Schema):
    type = fields.Str(required=True, validate=validate.OneOf([x for x in BuildConstants.AssessmentTypes]))
    questions = fields.Nested('AssessmentQuestionSchema', many=True)


class AssessmentQuestionSchema(Schema):
    type = fields.Str(required=True, validate=validate.OneOf([x for x in BuildConstants.QuestionTypes]))
    question = fields.Str(required=True)
    answer = fields.Str(required=False, description="The answer to the question for questions of type input")
    script = fields.Str(required=False, description="script name (e.g. attack.py)")
    script_language = fields.Str(required=False, description="e.g. python")
    server = fields.Str(required=False, description="Server that runs script. Takes server name from list of servers "
                                                    "provided above")
    operating_system = fields.Str(required=False, description="Target server operating system")
    complete = fields.Bool(default=False)


class EscapeRoomSchema(Schema):
    question = fields.Str(required=True, description="The door to open in the escape room")
    answer = fields.Str(required=False, description="Answer from the top level-question")
    puzzles = fields.Nested('PuzzleSchema', many=True)


class PuzzleSchema(Schema):
    type = fields.Str(required=True, validate=validate.OneOf([x for x in BuildConstants.QuestionTypes]))
    question = fields.Str(required=True)
    answer = fields.Str(required=False, description="The answer to the question for questions of type input")
    reveal = fields.Str(required=False, description="Information to reveal if they have the right answer")
