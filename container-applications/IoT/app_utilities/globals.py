from enum import Enum
from datetime import datetime, timezone, timedelta

class DatastoreKeyTypes(str, Enum):
    ADMIN_INFO = 'cybergym-admin-info'
    CLASSROOM = 'cybergym-class'
    FIXED_ARENA = 'fixed-arena'
    FIXED_ARENA_CLASS = 'fixed-arena-class'
    FIXED_ARENA_WORKSPACE = 'fixed-arena-workspace'
    CATALOG = 'v2-catalog'
    UNIT = 'v2-unit'
    WORKOUT = 'v2-workout'
    SERVER = 'cybergym-server'
    INSTRUCTOR = 'cybergym-instructor'
    CYBERARENA_ATTACK = 'cyberarena-attack'
    CYBERARENA_ATTACK_SPEC = 'cyberarena-attack-spec'
    IOT_DEVICE = 'cyberarena-iot-device'
    NVD_DATA = 'nvd_data'


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

    class AssessmentTypes(str, Enum):
        PERCENTAGE = "percentage"
        LEVEL = "level"

    class QuestionTypes(str, Enum):
        AUTO = "auto"
        INPUT = "input"
        UPLOAD = "upload"

    class Servers:
        FIXED_ARENA_WORKSPACE_PROXY = "display-workspace-server"

    class EscapeRoomEntryTypes(str, Enum):
        SERVER = 'server'
        WEB_APPLICATION = 'web_application'


class PubSub:
    class Topics(str, Enum):
        CYBER_ARENA = "cyber-arena"
        AGENT_TELEMETRY = 'agency-telemetry'
        IOT = 'cybergym-telemetry'

    class Handlers(str, Enum):
        BUDGET = "BUDGET"
        BUILD = "BUILD"
        MAINTENANCE = "MAINTENANCE"
        CONTROL = "CONTROL"
        ADMIN = "ADMIN"
        IOT = "IOT"
        AGENCY = "AGENCY"

    class Actions(Enum):
        BUILD = 1
        START = 2
        DELETE = 3
        STOP = 4
        REBUILD = 5
        SNAPSHOT = 6
        RESTORE = 7
        NUKE = 8
        START_ESCAPE_ROOM_TIMER = 9

    class CyberArenaObjects(Enum):
        FIXED_ARENA = 1
        FIXED_ARENA_CLASS = 2
        FIXED_ARENA_WORKSPACE = 3
        SERVER = 4
        AGENT_MACHINE = 5
        UNIT = 6
        WORKOUT = 7


class Commands:
    BASE = ['CLEAR', 'CONNECTED', 'HUMIDITY', 'PRESSURE', 'TEMP']
    HEALTHCARE = ['CRITICAL', 'HEART', 'PATIENT']
    CAR = ['BRAKE', 'GAS', "RADIO", "VEHICLE", 'PRODUCTS']
    COLORS = ['TEAL', 'RED', 'ORANGE', 'GREEN', 'PURPLE', 'WHITE', 'BLUE', 'YELLOW']
    MISC = ['SNAKE']

    @classmethod
    def get_all(cls):
        return cls.BASE + cls.HEALTHCARE + cls.CAR

    @classmethod
    def healthcare(cls, level):
        if level == 0:
            return [cls.BASE, cls.HEALTHCARE, cls.COLORS, cls.MISC]
        elif level == 1:
            return [cls.BASE, cls.COLORS]
        else:
            return cls.COLORS

    @classmethod
    def validate(cls, cmd, level):
        if level == 0:
            if cmd in cls.healthcare(0):
                return cmd
        elif level == 1:
            if cmd in cls.healthcare(1):
                return cmd
        else:
            if cmd in cls.healthcare(2):
                return cmd
        return False


def get_current_timestamp_utc(add_minutes=0):
    return (datetime.now(timezone.utc).replace(tzinfo=timezone.utc) + timedelta(minutes=add_minutes)).timestamp()
