"""
Parses yaml according to the Cyber Arena specification and stores a build structure in the cloud datastore.

We use marshmallow to perform serializer validation only. We define the required schemas in WorkoutComputeSchema,
WorkoutContainerSchema, ArenaSchema, and perhaps more. New fields in the yaml should be accounted for in the schema
validation.
"""

import calendar
import random
import string
import time
import validators
from datetime import datetime
from google.cloud import datastore
from marshmallow import Schema, fields, ValidationError
from utilities.globals import ds_client, student_instructions_url, teacher_instructions_url, workout_globals, \
    dns_suffix, LOG_LEVELS, BUILD_STATES, cloud_log, LogIDs, BuildTypes
from utilities.workout_validator import WorkoutValidator
from utilities.yaml_functions import parse_workout_yaml
from utilities.infrastructure_as_code.server_spec_to_cloud import ServerSpecToCloud
from utilities.infrastructure_as_code.student_entry_spec_to_cloud import StudentEntrySpecToCloud
from utilities.infrastructure_as_code.competition_server_spec_to_cloud import CompetitionServerSpecToCloud
from utilities.assessment_functions import CyberArenaAssessment
from utilities.infrastructure_as_code.additionaL_build_directives.student_network_combiner import StudentNetworkCombiner

__author__ = "Philip Huff"
__copyright__ = "Copyright 2021, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff", "Samuel Willis"]
__license__ = "MIT"
__version__ = "1.0.2"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Production"


class WorkoutComputeSchema(Schema):
    version = fields.Str(required=False)
    workout = fields.Dict()
    additional_build_directives = fields.Dict()
    student_entry = fields.Dict()
    networks = fields.List(fields.Dict())
    servers = fields.List(fields.Dict())
    routes = fields.List(fields.Dict(), required=False)
    firewall_rules = fields.List(fields.Dict(), required=False)
    assessment = fields.Dict(required=False)

    class Meta:
        strict = True


class WorkoutContainerSchema(Schema):
    version = fields.Str(required=False)
    workout = fields.Dict()
    container_info = fields.Dict()
    assessment = fields.Dict(required=False)

    class Meta:
        strict = True


class ArenaSchema(Schema):
    version = fields.Str(required=False)
    workout = fields.Dict()
    additional_networks = fields.List(fields.Dict())
    additional_servers = fields.List(fields.Dict())
    student_servers = fields.List(fields.Dict())
    additional_container_apps = fields.Dict()
    routes = fields.List(fields.Dict(), required=False)
    firewall_rules = fields.List(fields.Dict(), required=False)
    assessment = fields.Dict(required=False)

    class Meta:
        strict = True


class BuildSpecToCloud:
    def __init__(self, cyber_arena_yaml, unit_name, build_count, class_name, workout_length, email,
                 unit_id=None, build_now=True, registration_required=False, time_expiry=None):
        """
        Prepares the build of workouts based on a YAML specification by storing the information in the
        cloud datastore.
        :@param cyber_arena_yaml: The file name in the target cloud bucket that contains the build specification
        :@param build_type: Either a workout or arena
        :@param unit_name: A friendly name for the unit of workouts. A unit represents a classroom of students or teams
        :@param build_count: The number of workouts to build
        :@param class_name: the name of the class
        :@param workout_length: The number of days this workout will remain in the cloud project.
        :@param email: The email address of the instructor
        :@param unit_id: The unit id for the workout to be assigned to for addition to a pre-existing unit
        :@param build_now: Determine whether the cloud resources should be built now or wait until the
        student performs the workout. Default true because our workouts, historically, have all been built at the same
        time
        :@param workout_time_expiry: The timestamp expiration for this workout for more precise time expiration
        :@param type:
        :@param registration_required: Whether or not to require the assigned students to log in.
        :return: The unit_id AND the build type for the workout
        """
        self.spec_name = cyber_arena_yaml
        self.unit_name = unit_name
        self.build_count = build_count if int(build_count) < workout_globals.max_num_workouts \
            else workout_globals.max_num_workouts
        self.class_name = class_name
        self.email = email
        self.unit_id = unit_id
        self.build_now = build_now
        self.registration_required = registration_required
        self.workout_length = workout_length if int(workout_length) < workout_globals.max_workout_len \
            else workout_globals.max_workout_len
        max_time_expiry = calendar.timegm(time.gmtime()) + (86400 * workout_globals.max_workout_len)
        self.time_expiry = time_expiry if time_expiry and int(time_expiry) < max_time_expiry else max_time_expiry
        self.build_spec = parse_workout_yaml(cyber_arena_yaml)
        self.build_type = self.build_spec['workout'].get('build_type', 'compute')
        # Validate the build_spec before extracting the data
        self._validate_build_spec()
        # The workout key is common to all build types
        workout_spec = self.build_spec.get('workout', None)

        # Initialize build data
        self.workout_name = workout_spec.get('name', None)
        self.additional_build_directives = workout_spec.get('additional_build_directives', None)
        self.workout_description = workout_spec.get('workout_description')
        self.teacher_instructions_url = workout_spec.get('teacher_instructions_url', None)
        self.student_instructions_url = workout_spec.get('student_instructions_url', None)
        self._set_instructions_url()
        self.mapped_standards = workout_spec.get('standards', None)
        self.hourly_cost = workout_spec.get('hourly_cost', None)
        self.workout_author = workout_spec.get('author', None)

        # Initialize objects
        self.class_record = None
        self.build_keys = []
        self.cloud_ready_specs = []
        self.student_names = []
        self.student_emails = []
        self.unit_id = ''.join(random.choice(string.ascii_lowercase) for i in range(10))
        self._create_unit()
        if self.registration_required:
            self._process_class_roster()
        if self.build_type == BuildTypes.COMPUTE:
            self._parse_workout()
        elif self.build_type == BuildTypes.CONTAINER:
            self._parse_container()
        elif self.build_type == BuildTypes.ARENA:
            self._parse_arena()

    def commit_to_cloud(self):
        """
        Commits the parsed workout specification for multiple student builds to the cloud datastore.
        This first stores the unit to the datastore and then all the individual builds
        @return: None
        """
        cloud_log(LogIDs.MAIN_APP, f"Creating unit {self.unit_id}", LOG_LEVELS.INFO)
        new_unit = datastore.Entity(ds_client.key('cybergym-unit', self.unit_id))
        new_unit.update(self.new_unit)

        workout_ids = []
        for cloud_ready_spec in self.cloud_ready_specs:
            workout_id = ''.join(random.choice(string.ascii_lowercase) for i in range(10))
            workout_ids.append(workout_id)
            new_workout = datastore.Entity(ds_client.key('cybergym-workout', workout_id))
            new_workout.update(cloud_ready_spec)
            ds_client.put(new_workout)
            # Store the server specifications for compute workouts
            if self.build_type == BuildTypes.COMPUTE:
                self._commit_workout_servers(workout_id, new_workout)
        new_unit['workouts'] = workout_ids
        ds_client.put(new_unit)
        # If this is an arena, then store all server configurations at this time.
        if self.build_type == BuildTypes.ARENA:
            CompetitionServerSpecToCloud(unit=new_unit, workout_ids=workout_ids,
                                         workout_specs=self.cloud_ready_specs).commit_to_cloud()

        return {
            'unit_id': self.unit_id,
            'build_type': self.build_type
        }

    def _validate_build_spec(self):
        """
        Use the marshmallow schemas for validation only before using the data loaded from the yaml
        @param build_spec: Build specification pulled from the yaml
        @type build_spec:
        @return: None
        @rtype:
        """
        try:
            if self.build_type == BuildTypes.COMPUTE:
                validation_result = WorkoutComputeSchema().validate(self.build_spec)
            elif self.build_type == BuildTypes.CONTAINER:
                validation_result = WorkoutContainerSchema().validate(self.build_spec)
            elif self.build_type == BuildTypes.ARENA:
                validation_result = ArenaSchema().validate(self.build_spec)
        except ValidationError as err:
            error_message = f"Error when trying to load build specification of type {self.build_type}. " \
                            f"Validation errors: {err.messages}"
            cloud_log(LogIDs.MAIN_APP, error_message, LOG_LEVELS.ERROR)
            raise InvalidBuildSpecification(error_message)
        return

    def _set_instructions_url(self):
        student_instructions = self.student_instructions_url
        teacher_instructions = self.teacher_instructions_url
        if student_instructions and not self._validate_instructions_url(student_instructions):
            self.student_instructions_url = "%s%s" % (student_instructions_url, student_instructions)
        if teacher_instructions and not self._validate_instructions_url(teacher_instructions):
            self.teacher_instructions_url = "%s%s" % (teacher_instructions_url, teacher_instructions)

    def _validate_instructions_url(self, instruction_url: str) -> bool:
        """
        Validates instruction URL provided in spec file
        :return:
        """
        result = validators.url(instruction_url)
        if isinstance(result, validators.ValidationFailure):
            return False
        return result

    def _create_unit(self):
        self.new_unit = {
            "unit_name": self.unit_name,
            "build_type": self.build_type,
            "workout_name": self.workout_name,
            "instructor_id": self.email,
            'time_created': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'timestamp': str(calendar.timegm(time.gmtime())),
            "description": self.workout_description,
            "teacher_instructions_url": self.teacher_instructions_url,
            "workouts": [],
            "nice_standards": self.mapped_standards,
            "workout_author": self.workout_author,
            "hourly_cost": self.hourly_cost,
            "build_now": self.build_now,
            "registration_required": self.registration_required,
            "ready": True,
            'expiration': self.workout_length,
            'time_expiry': self.time_expiry,
        }

    def _parse_workout(self):
        networks = self.build_spec['networks']
        servers = self.build_spec['servers']
        student_entry = self.build_spec['student_entry']
        routes = self.build_spec.get('routes', None)
        firewall_rules = self.build_spec.get('firewall_rules', None)
        assessment = self.build_spec.get('assessment', None)

        # Verify server images exist in project compute before storing any data
        server_image_list = []
        for server in servers:
            if 'image' in server:
                server_image_list.append(server['image'])
        WorkoutValidator(image_list=server_image_list).validate_machine_images()
        for i in range(self.build_count):
            student_name = self.student_names[i] if self.student_names else None
            student_email = self.student_emails[i] if self.student_emails else None
            cloud_ready_spec = {
                'unit_id': self.unit_id,
                'workout_name': self.workout_name,
                'user_email': self.email,
                'student_instructions_url': self.student_instructions_url,
                'expiration': self.workout_length,
                'time_expiry': self.time_expiry,
                'build_type': BuildTypes.COMPUTE,
                'type': self.spec_name,
                'start_time': None,
                'run_hours': 0,
                'time_created': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'timestamp': str(calendar.timegm(time.gmtime())),
                'resources_deleted': False,
                'running': False,
                'misfit': False,
                'networks': networks,
                'servers': servers,
                'routes': routes,
                'firewall_rules': firewall_rules,
                'assessment': assessment,
                'complete': False,
                'student_entry': student_entry,
                'state': BUILD_STATES.START,
                'instructor_email': self.email,
                'student_name': student_name,
                'hourly_cost': self.hourly_cost,
                'registration_required': self.registration_required,
                'student_email': student_email
            }
            self.cloud_ready_specs.append(cloud_ready_spec)
        self._process_additional_build_directives()

    def _parse_container(self):
        container_info = self.build_spec['container_info']
        assessment = self.build_spec.get('assessment', None)
        host_name = self.build_spec['workout'].get('host_name', None)
        if not host_name:
            error_message = f"Container build does not contain a host name in its specification."
            cloud_log(LogIDs.MAIN_APP, error_message, LOG_LEVELS.ERROR)
            raise InvalidBuildSpecification(error_message)
        container_url = f"https://{host_name}{dns_suffix}"
        for i in range(self.build_count):
            student_name = self.student_names[i] if self.student_names else None
            student_email = self.student_emails[i] if self.student_emails else None

            cloud_ready_spec = {
                'unit_id': self.unit_id,
                'build_type': BuildTypes.CONTAINER,
                'type': self.spec_name,
                'workout_name': self.workout_name,
                'expiration': self.workout_length,
                'time_expiry': self.time_expiry,
                'container_url': container_url,
                'student_instructions_url': self.student_instructions_url,
                'time_created': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'timestamp': str(calendar.timegm(time.gmtime())),
                'complete': False,
                'container_info': container_info,
                'assessment': assessment,
                'state': BUILD_STATES.RUNNING,
                'instructor_email': self.email,
                'student_name': student_name,
                'registration_required': self.registration_required,
                'student_email': student_email
            }
            self.cloud_ready_specs.append(cloud_ready_spec)

    def _parse_arena(self):
        networks = self.build_spec.get('additional-networks', None)
        servers = self.build_spec.get('additional-servers', None)
        containers = self.build_spec.get('additional-container-apps', None)
        routes = self.build_spec.get('routes', None)
        firewall_rules = self.build_spec.get('firewall_rules', None)
        student_servers = self.build_spec['student-servers']['servers']
        student_entry = self.build_spec['student-servers']['student_entry']
        student_entry_type = self.build_spec['student-servers']['student_entry_type']
        student_entry_username = self.build_spec['student-servers']['student_entry_username']
        student_entry_password = self.build_spec['student-servers']['student_entry_password']
        network_type = self.build_spec['student-servers']['network_type']
        assessment = self.build_spec.get('assessment', None)

        # Verify server images exist in project compute before storing any data
        server_image_list = [server['image'] for server in student_servers]
        WorkoutValidator(image_list=server_image_list).validate_machine_images()

        # Add an arena specification to the unit
        self.new_unit['arena'] = {
            'expiration': self.workout_length,
            'expiry': self.time_expiry,
            'start_time': None,
            'run_hours': 0,
            'time_created': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'timestamp': str(calendar.timegm(time.gmtime())),
            'resources_deleted': False,
            'running': False,
            'misfit': False,
            'networks': networks,
            'servers': servers,
            'routes': routes,
            'firewall_rules': firewall_rules,
            'student_entry': student_entry,
            'student_entry_type': student_entry_type,
            'student_entry_username': student_entry_username,
            'student_entry_password': student_entry_password,
            'student_network_type': network_type
        }

        for i in range(self.build_count):
            student_name = self.student_names[i] if self.student_names else None
            student_email = self.student_emails[i] if self.student_emails else None
            cloud_ready_spec = {
                'unit_id': self.unit_id,
                'type': self.spec_name,
                'build_type': BuildTypes.ARENA,
                'student_instructions_url': self.student_instructions_url,
                'start_time': None,
                'run_hours': 0,
                'time_created': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'timestamp': str(calendar.timegm(time.gmtime())),
                'running': False,
                'misfit': False,
                'assessment': assessment,
                'student_servers': student_servers,
                'containers': containers,
                'instructor_id': self.email,
                'state': BUILD_STATES.START,
                'student_name': student_name,
                'registration_required': self.registration_required,
                'student_email': student_email
            }
            self.cloud_ready_specs.append(cloud_ready_spec)

    def _process_class_roster(self):
        class_list = ds_client.query(kind='cybergym-class')
        class_list.add_filter('teacher_email', '=', self.email)
        class_list.add_filter('class_name', '=', self.class_name)
        self.class_record = list(class_list.fetch())[0]
        for student_name in self.class_record['roster']:
            if self.class_record['student_auth'] == 'email':
                self.student_emails.append(student_name['student_email'])
            self.student_names.append(student_name)

    def _cloud_update_class(self):
        class_unit = {
            "unit_id": self.unit_id,
            "unit_name": self.unit_name,
            "workout_name": self.workout_name,
            "build_type": self.build_type,
            "timestamp": str(calendar.timegm(time.gmtime()))
        }
        if 'unit_list' not in self.class_record:
            unit_list = []
            unit_list.append(class_unit)
            self.class_record['unit_list'] = unit_list
        else:
            self.class_record['unit_list'].append(class_unit)
        ds_client.put(self.class_record)

    def _commit_workout_servers(self, workout_id, new_workout):
        """
        Store the server specifications of the servers in this workout as well as the student entry guacamole server
        @param workout_id: ID of the new workout
        @type workout_id: str
        @param new_workout: Datastore dict of the new workout
        @type new_workout: dict
        @return: None
        """
        startup_scripts = None
        if new_workout['assessment']:
            startup_scripts = CyberArenaAssessment.get_startup_scripts(workout_id=workout_id,
                                                                       assessment=new_workout['assessment'])
        for server in new_workout['servers']:
            ServerSpecToCloud(server, workout_id, startup_scripts).commit_to_cloud()
        StudentEntrySpecToCloud(type=BuildTypes.COMPUTE, build=new_workout, build_id=workout_id).commit_to_cloud()

    def _process_additional_build_directives(self):
        if self.additional_build_directives:
            combine_student_networks = self.additional_build_directives.get('combine_student_networks', None)
            if combine_student_networks:
                StudentNetworkCombiner(self.cloud_ready_specs, combine_student_networks).combine_network

class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class InvalidBuildSpecification(Error):
    """Exception raised for errors in the input.

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """
    def __init__(self, message):
        self.message = message
