from marshmallow import Schema, fields, validate
import uuid

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
    creation_timestamp = fields.Float()
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
    add_attacker = fields.Bool(description="Whether to add an attacker (agent) machine to the workspace networks",
                               default=False)
    test = fields.Bool(required=False, description="Whether the Fixed Arena Class is a test. This helps in cleaning the datastore.")


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
    lms_connection = fields.Nested('LMSConnectionSchema', required=False,
                                   description="The information needed to connect a lab to a course")
    lms_quiz = fields.Nested('LMSQuizSchema', required=False)
    escape_room = fields.Nested('EscapeRoomSchema', required=False,
                                description="Escape room units include additional specification of the escape room "
                                            "puzzles associated with each workout")
    test = fields.Bool(required=False, description="Whether the unit is a test. This helps in cleaning the datastore.")
    join_code = fields.Str(required=False, description='Used to invite students to claim a unit workspace')
    workout_duration_days = fields.Int(required=False,
                                       description='For asynchronous workout builds, specify to add an expiration '
                                                   'timestamp for the workout. This is used for long running units '
                                                   'where students complete workouts asynchronously.')


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
    standard_mappings = fields.Nested('StandardMappingsSchema', many=True, required=False,
                                      description='Curriculum standard mappings for this lab')
    tags = fields.Nested('TeachingConceptsSchema', many=True, required=False, default=[],
                         description='Key concepts that this build is intended to teach')

    class Meta:
        strict = True


class TeachingConceptsSchema(Schema):
    id = fields.Str(required=True, validate=validate.OneOf([x.name.lower() for x in BuildConstants.TeachingConcepts]))
    name = fields.Str(required=True, validate=validate.OneOf([x.value for x in BuildConstants.TeachingConcepts]))

    class Meta:
        strict = True


class StandardMappingsSchema(Schema):
    framework = fields.Str(required=True, validate=validate.OneOf([x.value for x in BuildConstants.Frameworks]))
    mapping = fields.Str(required=True)

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
    hidden = fields.Bool(default=False, description="Whether to display this server to students or not.")
    machine_type = fields.Str(required=True, default="e1-standard1")
    add_disk = fields.Int(required=False, default=0)
    tags = fields.List(fields.Str)
    build_type = fields.Str(default=None)
    metadata = fields.Str(default=None)
    sshkey = fields.Str(default=None)
    can_ip_forward = fields.Bool(default=False)
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
    dns_host_suffix = fields.Str(required=False)
    ip_aliases = fields.List(fields.Str, required=False)

    class Meta:
        strict = True


class HumanInteractionSchema(Schema):
    display = fields.Bool(default=False)
    protocol = fields.Str(required=True, validate=validate.OneOf([x for x in BuildConstants.Protocols]))
    username = fields.Str()
    password = fields.Str()
    domain = fields.Str()
    security_mode = fields.Str(default=BuildConstants.SecurityModes.NLA,
                               validate=validate.OneOf([x for x in BuildConstants.SecurityModes]))


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
    questions = fields.Nested('AssessmentQuestionSchema', many=True)
    assessment_script = fields.Nested('AssessmentScriptSchema',
                                      description="The assessment script for all indicated questions. The script must "
                                                  "align with answering the given questions.")
    key = fields.Str(required=False, description='Key used for decrypting workout secrets in container applications')


class LMSQuizSchema(Schema):
    type = fields.Str(required=False, description="Practice quiz or assignment")
    due_at = fields.DateTime(required=False, description="Due date for assignment")
    description = fields.Str(required=False, description="Description of assignment")
    allowed_attempts = fields.Float(missing=-1.0, description="Attempts available for assignment, -1 is unlimited")
    assessment_script = fields.Nested('AssessmentScriptSchema', required=False,
                                      description="The assessment script for all indicated questions. The script must "
                                                  "align with answering the given questions.")
    questions = fields.Nested('LMSQuizQuestionsSchema', many=True)


class AssessmentQuestionSchema(Schema):
    id = fields.Str(missing=lambda: str(uuid.uuid4()), description="An ID to use when referring to specific questions")
    name = fields.Str(required=False, description="The name of the question, which is also used for the workout-level "
                                                  "assessment script.")
    type = fields.Str(required=True, validate=validate.OneOf([x for x in BuildConstants.QuestionTypes]))
    question = fields.Str(required=True)
    key = fields.Str(required=False, description='The value used for decrypting individual cryptographic questions')
    answer = fields.Str(required=False, description="The answer to the question for questions of type input")
    script_assessment = fields.Bool(missing=False)
    complete = fields.Bool(missing=False)


class AssessmentScriptSchema(Schema):
    script = fields.Str(required=False, description="script name (e.g. attack.py)")
    script_language = fields.Str(required=False, description="e.g. python")
    server = fields.Str(required=False, description="Server that runs script. Takes server name from list of servers "
                                                    "provided above")
    operating_system = fields.Str(required=False, description="Target server operating system")


class LMSConnectionSchema(Schema):
    lms_type = fields.Str(required=True, validate=validate.OneOf([x for x in BuildConstants.LMS]),
                          description="The type of LMS this should integrate with.")
    api_key = fields.Str(required=True, description="The API key from the user profile needed for connecting to "
                                                    "the LMS")
    url = fields.Str(required=True, description="The LMS API URL")
    course_code = fields.Int(required=True, description="The course code to use for creating the quiz")


class LMSQuizQuestionsSchema(Schema):
    name = fields.Str(required=False, description="Question name")
    question_text = fields.Str(required=True, description="Question text")
    question_type = fields.Str(required=False, description="Question type")
    points_possible = fields.Float(required=False, description="Points")
    script_assessment = fields.Bool(missing=False)
    bonus = fields.Bool(required=False, description="Whether to count this question as a bonus")
    answers = fields.Nested('LMSQuizAnswerSchema', many=True, description="Question answers")
    complete = fields.Bool(required=False,
                           description="Used to mark completion for multi-step auto assessment scripts")


class LMSQuizAnswerSchema(Schema):
    answer_text = fields.Str(required=False, description="Question text")
    weight = fields.Float(missing=0.0)


class EscapeRoomSchema(Schema):
    question = fields.Str(required=True, description="The door to open in the escape room")
    answer = fields.Str(description="Answer from the top level-question")
    responses = fields.List(fields.Str(), missing=[], description="Records the team's attempts to answer the question "
                                                                  "and escape")
    escaped = fields.Bool(missing=False, description="Whether or not the team has successfully escaped")
    time_limit = fields.Int(missing=3600, description="Number of seconds the team has to escape from the room")
    start_time = fields.Float(missing=0.0, description="When the escape room started. This will be used to calculate "
                                                       "remaining time")
    remaining_time = fields.Float(required=False)
    puzzles = fields.Nested('PuzzleSchema', many=True)


class PuzzleSchema(Schema):
    id = fields.Str(missing=lambda: str(uuid.uuid4()), description="An ID to use when referring to specific puzzles")
    instructions_url = fields.Str(required=False, allow_none=True)
    entry_type = fields.Str(required=False, validate=validate.OneOf([x for x in BuildConstants.EscapeRoomEntryTypes]),
                            description="The type of entry to present to the user for solving the question "
                                        "(e.g., server or web_application)")
    entry_name = fields.Str(required=False, description="A name based on the entry_type to help build a URL for the "
                                                       "student to click on. For example, a server will have it's "
                                                       "human interaction guacamole link that they can click on to "
                                                       "answer the question")
    type = fields.Str(missing=BuildConstants.QuestionTypes.INPUT,
                      validate=validate.OneOf([x for x in BuildConstants.QuestionTypes]))
    summary = fields.Str(required=False, description='Brief outline of what the puzzle is about')
    question = fields.Str(required=True)
    name = fields.Str(requied=True)
    answer = fields.Str(required=False, description="The answer to the question for questions of type input")
    script = fields.Str(required=False, description="script name (e.g. attack.py)")
    script_language = fields.Str(required=False, description="e.g. python")
    server = fields.Str(required=False, description="Server that runs script. Takes server name from list of servers "
                                                    "provided above")
    operating_system = fields.Str(required=False, description="Target server operating system")
    responses = fields.List(fields.Str(), missing=[],
                            description="Records the team's attempts to answer the question and escape")
    correct = fields.Bool(missing=False, description="Whether the puzzle response is correct")
    reveal = fields.Str(required=False, description="Information to reveal if they have the right answer")