from enum import Enum


class DatastoreKeyTypes(str, Enum):
    CYBERGYM_WORKOUT = 'cybergym-workout'
    FIXED_ARENA = 'fixed-arena'
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

    class ReservedIPAddresses:
        DISPLAY_SERVER = '10.1.0.3'

    GATEWAY_NETWORK = {
            'name': 'gateway',
            'subnets': [
                {
                    'name': 'default',
                    'ip_subnet': '10.1.0.0/24'
                }
            ]
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

    class Handlers(str, Enum):
        BUDGET = "BUDGET"
        BUILD = "BUILD"
        MAINTENANCE = "MAINTENANCE"
        ADMIN = "ADMIN"
        IOT = "IOT"
        BOTNET = "BOTNET"

    class Actions(str, Enum):
        BUILD_SERVER = 'BUILD_SERVER'
        START_SERVER = 'START_SERVER'
        DELETE_SERVER = 'DELETE_SERVER'
        STOP_SERVER = 'STOP_SERVER'
        REBUILD_SERVER = 'REBUILD_SERVER'
        SNAPSHOT_SERVER = 'SNAPSHOT_SERVER'
        RESTORE_SERVER = 'RESTORE_SERVER'
        BUILD_DISPLAY_PROXY = 'BUILD_DISPLAY_PROXY'
        BUILD_FIREWALL_SERVER = 'BUILD_FIREWALL_SERVER'
