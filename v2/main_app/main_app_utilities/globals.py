from enum import Enum
from datetime import datetime, timezone, timedelta


class DatastoreKeyTypes(str, Enum):
    ADMIN_INFO = 'cybergym-admin-info'
    CLASSROOM = 'cybergym-class'
    CYBERGYM_WORKOUT = 'cybergym-workout'
    CYBERGYM_UNIT = 'cybergym-unit'
    FIXED_ARENA = 'fixed-arena'
    FIXED_ARENA_CLASS = 'fixed-arena-class'
    FIXED_ARENA_WORKSPACE = 'fixed-arena-workspace'
    SERVER = 'cybergym-server'
    INSTRUCTOR = 'cybergym-instructor'
    CYBERARENA_ATTACK = 'cyberarena-attack'
    CYBERARENA_ATTACK_SPEC = 'cyberarena-attack-spec'
    IOT_DEVICE = 'cybergym-iot-device'


class BuildConstants:
    class BuildType(str, Enum):
        ARENA = "arena"
        FIXED_ARENA = "fixed_arena"
        FIXED_ARENA_CLASS = "fixed_arena_class"
        FIXED_ARENA_WORKSPACE = "fixed_arena_workspace"
        WORKOUT = "workout"
        FIXED_ARENA_WEAKNESS = 'fixed_arena_weakness'
        FIXED_ARENA_ATTACK = 'fixed_arena_attack'

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
            FIXED_ARENA_WORKOUT_SERVER_RANGE = ('10.1.0.10', '10.1.0.200')
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


class PubSub:
    class Topics(str, Enum):
        CYBER_ARENA = "cyber-arena"

    class Handlers(str, Enum):
        BUDGET = "BUDGET"
        BUILD = "BUILD"
        MAINTENANCE = "MAINTENANCE"
        CONTROL = "CONTROL"
        ADMIN = "ADMIN"
        IOT = "IOT"
        BOTNET = "BOTNET"

    class BuildActions(Enum):
        WORKOUT = 0
        ARENA = 1
        FIXED_ARENA = 2
        FIXED_ARENA_CLASS = 3
        SERVER = 4
        DISPLAY_PROXY = 5
        FIREWALL_SERVER = 6
        FIXED_ARENA_WORKSPACE_PROXY = 7

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


class Buckets:
    class Folders(str, Enum):
        SPECS = "specs/"


def get_current_timestamp_utc(add_minutes=0):
    return (datetime.now(timezone.utc).replace(tzinfo=timezone.utc) + timedelta(minutes=add_minutes)).timestamp()
