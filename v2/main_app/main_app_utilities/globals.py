from enum import Enum
from datetime import datetime, timezone, timedelta


class DatastoreKeyTypes(str, Enum):
    ADMIN_INFO = 'cybergym-admin-info'
    CLASSROOM = 'cybergym-class'
    FIXED_ARENA = 'fixed-arena'
    FIXED_ARENA_CLASS = 'fixed-arena-class'
    FIXED_ARENA_WORKSPACE = 'fixed-arena-workspace'
    UNIT = 'v2-unit'
    WORKOUT = 'v2-workout'
    SERVER = 'cybergym-server'
    INSTRUCTOR = 'cybergym-instructor'
    CYBERARENA_ATTACK = 'cyberarena-attack'
    CYBERARENA_ATTACK_SPEC = 'cyberarena-attack-spec'
    IOT_DEVICE = 'cybergym-iot-device'


class BuildConstants:
    class BuildType(str, Enum):
        AGENT_MACHINE = "agent_machine"
        FIXED_ARENA = "fixed_arena"
        FIXED_ARENA_CLASS = "fixed_arena_class"
        FIXED_ARENA_WORKSPACE = "fixed_arena_workspace"
        UNIT = "unit"
        WORKOUT = "workout"
        FIXED_ARENA_WEAKNESS = 'fixed_arena_weakness'
        FIXED_ARENA_ATTACK = 'fixed_arena_attack'
        ESCAPE_ROOM = 'escape_room'

    class Protocols(str, Enum):
        RDP = "rdp"
        VNC = "vnc"

    class Firewalls(str, Enum):
        FORTINET = "fortinet"
        VYOS = "vyos"

    class TransportProtocols(str, Enum):
        TCP = "tcp"
        UDP = "udp"
        ICMP = "icmp"

    class MachineTypes(Enum):
        VERY_SMALL = 0
        SMALL = 1
        MEDIUM = 2
        LARGE = 3
        VERY_LARGE = 4
        ROUTER = 5

    class MachineImages:
        GUACAMOLE = "image-labentry"
        FORTIMANAGER = "image-fortimanager"
        AGENT = 'image-cybergym-kali'

    class AssessmentTypes(str, Enum):
        PERCENTAGE = "percentage"
        LEVEL = "level"

    class QuestionTypes(str, Enum):
        AUTO = "auto"
        INPUT = "input"
        UPLOAD = "upload"

    class ServerBuildType:
        MACHINE_IMAGE = "machine-image"

    class Networks:
        class Reservations:
            DISPLAY_SERVER = '10.1.0.3'
            WORKSPACE_PROXY_SERVER = '10.1.0.4'
            WORKOUT_PROXY_SERVER = "10.1.1.3"
            FIXED_ARENA_WORKOUT_SERVER_RANGE = ('10.1.0.10', '10.1.0.200')
            AGENT_MACHINE = '10.1.0.210'
        GATEWAY_NETWORK_NAME = 'gateway'
        GATEWAY_NETWORK_CONFIG = {
            'name': GATEWAY_NETWORK_NAME,
            'subnets': [
                {
                    'name': 'default',
                    'ip_subnet': '10.1.0.0/24'
                }
            ]
        }
        WORKOUT_EXTERNAL_NAME = 'external'

    class Servers:
        FIXED_ARENA_WORKSPACE_PROXY = "display-workspace-server"

    class FixedArenaStates(Enum):
        START = 0
        BUILDING_ASSESSMENT = 1
        BUILDING_NETWORKS = 2
        COMPLETED_NETWORKS = 3
        BUILDING_SERVERS = 4
        COMPLETED_SERVERS = 5
        BUILDING_FIREWALL = 6
        COMPLETED_FIREWALL = 7
        BUILDING_ROUTES = 8
        COMPLETED_ROUTES = 9
        BUILDING_FIREWALL_RULES = 10
        COMPLETED_FIREWALL_RULES = 11
        BUILDING_STUDENT_ENTRY = 12
        COMPLETED_STUDENT_ENTRY = 13
        GUACAMOLE_SERVER_LOAD_TIMEOUT = 28
        RUNNING = 50
        STOPPING = 51
        STARTING = 52
        READY = 53
        EXPIRED = 60
        MISFIT = 61
        BROKEN = 62
        DELETING_SERVERS = 70
        COMPLETED_DELETING_SERVERS = 71
        DELETED = 72

    class FixedArenaClassStates(Enum):
        START = 0
        BUILDING_ASSESSMENT = 1
        BUILDING_WORKSPACE_SERVERS = 3
        BUILDING_WORKSPACE_PROXY = 4
        COMPLETED_BUILDING_SERVERS = 5
        BUILDING_ROUTES = 8
        COMPLETED_ROUTES = 9
        BUILDING_FIREWALL_RULES = 10
        COMPLETED_FIREWALL_RULES = 11
        PROXY_SERVER_TIMEOUT = 28
        RUNNING = 50
        STOPPING = 51
        STARTING = 52
        READY = 53
        EXPIRED = 60
        MISFIT = 61
        BROKEN = 62
        DELETING_SERVERS = 70
        COMPLETED_DELETING_SERVERS = 71
        DELETED = 72


class WorkoutStates(Enum):
    START = 0
    BUILDING_ASSESSMENT = 1
    BUILDING_NETWORKS = 2
    COMPLETED_NETWORKS = 3
    BUILDING_SERVERS = 4
    COMPLETED_SERVERS = 5
    BUILDING_FIREWALL = 6
    COMPLETED_FIREWALL = 7
    BUILDING_ROUTES = 8
    COMPLETED_ROUTES = 9
    BUILDING_FIREWALL_RULES = 10
    COMPLETED_FIREWALL_RULES = 11
    BUILDING_STUDENT_ENTRY = 12
    COMPLETED_STUDENT_ENTRY = 13
    GUACAMOLE_SERVER_LOAD_TIMEOUT = 28
    RUNNING = 50
    STOPPING = 51
    STARTING = 52
    READY = 53
    EXPIRED = 60
    MISFIT = 61
    BROKEN = 62
    DELETING_SERVERS = 70
    COMPLETED_DELETING_SERVERS = 71
    DELETED = 72


class PubSub:
    class Topics(str, Enum):
        CYBER_ARENA = "cyber-arena"
        AGENT_TELEMETRY = 'agency-telemetry'


    class Handlers(str, Enum):
        BUDGET = "BUDGET"
        BUILD = "BUILD"
        MAINTENANCE = "MAINTENANCE"
        CONTROL = "CONTROL"
        ADMIN = "ADMIN"
        IOT = "IOT"
        AGENCY = "AGENCY"

    class BuildActions(Enum):
        WORKOUT = 0
        UNIT = 1
        FIXED_ARENA = 2
        FIXED_ARENA_CLASS = 3
        SERVER = 4
        DISPLAY_PROXY = 5
        FIREWALL_SERVER = 6
        FIXED_ARENA_WORKSPACE_PROXY = 7
        CYBER_ARENA_AGENT = 9
        CYBER_ARENA_ATTACK = 10
        CYBER_ARENA_WEAKNESS = 11

    class Actions(Enum):
        BUILD = 1
        START = 2
        DELETE = 3
        STOP = 4
        REBUILD = 5
        SNAPSHOT = 6
        RESTORE = 7
        NUKE = 8

    class CyberArenaObjects(Enum):
        FIXED_ARENA = 1
        FIXED_ARENA_CLASS = 2
        FIXED_ARENA_WORKSPACE = 3
        SERVER = 4
        AGENT_MACHINE = 5
        UNIT = 6
        WORKOUT = 7


class Buckets:
    class Folders(str, Enum):
        SPECS = "specs/"


def get_current_timestamp_utc(add_minutes=0):
    return (datetime.now(timezone.utc).replace(tzinfo=timezone.utc) + timedelta(minutes=add_minutes)).timestamp()
