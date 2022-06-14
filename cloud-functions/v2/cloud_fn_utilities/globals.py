from enum import Enum


class DatastoreKeyTypes(str, Enum):
    CYBERGYM_WORKOUT = 'cybergym-workout'
    FIXED_ARENA = 'fixed-arena'
    FIXED_ARENA_WORKOUT = 'fixed-arena-workout'
    SERVER = 'cybergym-server'
    ADMIN_INFO = 'cybergym-admin-info'


class BuildConstants:
    class BuildType(str, Enum):
        ARENA = "arena"
        FIXED_ARENA = "fixed_arena"
        FIXED_ARENA_WORKOUT = "fixed_arena_workout"
        WORKOUT = "workout"

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


class PubSub:
    class Topics(str, Enum):
        CYBER_ARENA = "cyber-arena"

    class Handlers(str, Enum):
        BUDGET = "BUDGET"
        BUILD = "BUILD"
        MAINTENANCE = "MAINTENANCE"
        ADMIN = "ADMIN"
        IOT = "IOT"
        BOTNET = "BOTNET"

    class BuildActions(Enum):
        WORKOUT = 0
        ARENA = 1
        FIXED_ARENA = 2
        FIXED_ARENA_WORKOUT = 3
        SERVER = 4
        DISPLAY_PROXY = 5
        FIREWALL_SERVER = 6
        FIXED_ARENA_WORKSPACE_PROXY = 7

    class MaintenanceActions(Enum):
        START_SERVER = 5
        DELETE_SERVER = 6
        STOP_SERVER = 7
        REBUILD_SERVER = 8
        SNAPSHOT_SERVER = 9
        RESTORE_SERVER = 10

