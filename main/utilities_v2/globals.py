from enum import Enum


class DatastoreKeyTypes(str, Enum):
    CYBERGYM_WORKOUT = 'cybergym-workout'
    FIXED_ARENA = 'fixed-arena'
    SERVER = 'cybergym-server'


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

    class ReservedIPAddresses:
        DISPLAY_SERVER = '10.1.0.3'

    GATEWAY_NETWORK = {
        'name': 'gateway',
        'subnets':
            {
                'name': 'default',
                'ip_subnet': '10.1.0.0/24'
            }
    }

    class ServerBuildType:
        MACHINE_IMAGE = "machine-image"


class PubSub:
    class Topics(str, Enum):
        MANAGE_SERVER = 'manage-server'
        DELETE_EXPIRED = 'maint-del-tmp-systems'
        BUILD_WORKOUT = 'build-workouts'
        BUILD_ARENA = 'build-arena'
        BUILD_FIXED_ARENA = "build-fixed-arena"

    class ServerActions(str, Enum):
        BUILD = 'BUILD'
        START = 'START'
        DELETE = 'DELETE'
        STOP = 'STOP'
        REBUILD = 'REBUILD'
        SNAPSHOT = 'SNAPSHOT'
        RESTORE = 'RESTORE'

class Buckets:
    class Folders(str, Enum):
        FIXED_ARENA = "yaml-build-files/v2/fixed_arena/"