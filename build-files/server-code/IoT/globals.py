from enum import Enum


class Configuration:
    TELEMETRY = '/usr/src/cyberarena-dev/telemetry.log'
    CERTS = {
        'ssl_private_key': '/usr/src/cyberarena-dev/local/iot_private.pem',
        'algorithm': 'RS256',
        'root_cert': '/usr/src/cyberarena-dev/local/roots.pem',
    }
    PROJECT = {
        'project_id': 'virtual-arkansas',
        'zone': 'us-central1',
        'registry_id': 'cybergym-registry',
        'device_id': 'cybergym-rasbpi3'
    }


class Files:
    class Images:
        heart = '/usr/src/cyberarena-dev/images/heart/'
        heartrate = '/usr/src/cyberarena-dev/images/heartrate/'
        arrow = '/usr/src/cyberarena-dev/images/arrow/'
        road = '/usr/src/cyberarena-dev/images/road/'
        alerts = '/usr/src/cyberarena-dev/images/alerts/'
        faces = '/usr/src/cyberarena-dev/images/faces/'
        phase = '/usr/src/cyberarena-dev/images/phase/'
        lock = '/usr/src/cyberarena-dev/images/lock/'
        logo = '/usr/src/cyberarena-dev/images/logo/'

    class Data:
        car = '/usr/src/cyberarena-dev/data/tesla.json'
        patients = '/usr/src/cyberarena-dev/data/patients.json'
        stations = '/usr/src/cyberarena-dev/data/radio_stations.json'


class Iot:
    class DisplayColors(Enum):
        RED = [255, 0, 0]
        ORANGE = [255, 69, 0]
        YELLOW = [255, 255, 0]
        GREEN = [0, 255, 0]
        BLUE = [0, 0, 128]
        PURPLE = [204, 0, 204]
        WHITE = [255, 255, 255]
        TEAL = [51, 255, 153]

        @classmethod
        def get(cls, value):
            for i in cls:
                if i.name == value:
                    return i.value
            return False

        @classmethod
        def to_dict(cls):
            return {i.name: i.value for i in cls}

    class Commands:
        # Base Commands
        CLEAR = 'CLEAR'
        CONNECTED = 'CONNECTED'

        # Sensory Commands
        HUMIDITY = 'HUMIDITY'
        PRESSURE = 'PRESSURE'
        TEMP = 'TEMP'

        # Healthcare Commands
        CRITICAL = 'CRITICAL'
        HEART = 'HEART'
        PATIENTS = 'PATIENT'

        # Self Driving car commands
        BRAKE = 'BRAKE'
        GAS = 'GAS'
        RADIO = 'RADIO'
        IAMSPEED = 'IAMSPEED'
        VEHICLE = 'VEHICLE'
        CAR_USER = 'USER'
        PRODUCTS = 'PRODUCTS'
        TRIP = 'TRIP_PLANNER'

        # Misc
        SNAKE = 'SNAKE'
        ALL = 'ALL'
