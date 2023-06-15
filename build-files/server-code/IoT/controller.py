# UA Little Rock CyberArena
# 
# SenseHatController.py
# Authors: Andrew Bomberger
# 
# This class utilizes the SenseHat modules to interact with
# the Raspberry Pi and SenseHat board. 
# 
# For testing, you don't need the physical SenseHat board. 
# You'll need to start the SenseHat Emulator first and then 
# import the module using:
#   from sense_emu import SenseHat
# Functionally, this doesn't change any following code other
# than redirecting all commands through the emulator instead
# of the physical board.
import logging
import random
import math
import os
import yaml
from dotenv import load_dotenv
from enum import Enum
from sense_hat import SenseHat
from time import sleep, time
from image_maps import ImageMaps
from system_status import SystemInfo
from globals import Iot, Files, Configuration
from tesla_iot import TeslaIoT
import json

# load project settings into config var
# with open('/usr/src/cyberarena-dev/config.yaml') as file:
#    config = yaml.full_load(file)
load_dotenv()

# initialize logger
logging.basicConfig(
        filename=Configuration.TELEMETRY,
        format="%(asctime)s [%(levelname)s] %(funcName)s: %(message)s",
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M')


class Secrets(Enum):
    ACCEL_CRIT = 'CyberArena{eVRwYtFNdRVIVlfC}'
    CURIOUS = 'CyberArena{DrjaGZ1NhkhoOMJr}'
    CURIOUS2 = 'CyberArena{SocialUnsecurityNumbers}'
    PATIENT_CRIT = 'CyberArena{IDontFeelSoGoodMrStark}'

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_

    @classmethod
    def get(cls, value):
        if cls.has_value(value):
            return cls[value].value
        return False


class SenseHatControls(object):
    """
        Controller class to utilize SenseHat
        board
    """
    def __init__(self, init_time, sys_info, **kwargs):
        # Init/Configure SenseHat object
        self.sense_hat = SenseHat()
        self.sense_hat.clear()
        self.sense_hat.low_light = True
        # imu config => (Compass, Gyroscope, Accelerometer)
        self.sense_hat.set_imu_config(False, True, True)
        # SenseHat display State
        self.state = False
        # System variables
        self.system_info = sys_info
        self.sys_time = init_time

        self.colors = Iot.DisplayColors.to_dict()

        # SenseHat sensory and data variables
        # accel data
        self.accel = self.get_accel 
        self.brake = -10

        # sensory data
        self.humidity = self.get_humidity        
        self.pressure = self.get_pressure
        self.temp = self.get_temp

        # misc data
        self.heartrate = self.get_heartrate
        self.secrets = Secrets

        # unlock data
        self.combination = ['.....', '--...', '..---', '-----']
        self.combination_str = (" ").join(self.combination)

    def process_thread_msg(self, msg):
        cmd = msg[0]
        logging.info(f'Thread processing  msg: {msg}')
        # TODO: Add heart_critical, and radio methods
        sense_commands = {
            'CRITICAL': self.heart_critical,
            'CONNECTED': self.connected,
            'HEART': self.display_heartrate,
            'HUMIDITY': self.display_humidity,
            'PRESSURE': self.display_pressure,
            'SNAKE': self.snake,
            'PATIENTS': self.display_ssn,
            'TEMP': self.display_temp,
            'UNLOCK': self.display_combination,
        }
        car_commands = {
            'BRAKE': self.display_accel_brake,
            'CLEAR': self.clear_display,
            'GAS': self.display_accel,
            'IAMSPEED': self.accel_critical,
            'RADIO': self.radio,
            'CAR_USER': self.car_user,
            'VEHICLE': self.vehicle,
            'PRODUCTS': self.products,
            'TRIP': self.trip_planner,
        }
        if cmd in sense_commands:
            if cmd == 'HEART':
                sense_commands[cmd](heartrate=msg[1]) 
            else:
                sense_commands[cmd]()
        elif cmd in self.colors:
            self.display_color(cmd)
        elif cmd in car_commands:
            car_commands[cmd]()
        elif cmd == 'ALL':
            return self.list_commands()
        else:
            return

    def clear_display(self):
        self.sense_hat.clear()
        return 'Display cleared!'

    def calibrate_orientation(self):
        accel = self.sense_hat.accel
        with open('./.env', 'w') as f:
            string = f"X={accel['roll']}\nY={accel['pitch']}\nZ={accel['yaw']}\n"
            f.write(string)
    
    @property
    def get_accel(self):
        """
            Uses built-in accelerometer to measure accelerance in terms of G's and returns
            speed. Since we are not able to travel any noticable speeds while connected to 
            a wall, speed is multiplied by a larger value to emulate higher movement speeds.
        """
        # {'roll': 303.34583138207574, 'pitch': 0.6313056338044045, 'yaw': 0.0007390659989990934}i
        # Zero out the sensor
        base_x = int(os.getenv('X').split(".")[0]) / 120
        base_y = int(os.getenv('Y').split(".")[0]) / 120
        base_z = int(os.getenv('Z').split(".")[0]) / 120
        # get accelermoter data
        accel = self.sense_hat.accel
        avg_x = accel['roll'] / 120
        avg_y = accel['pitch'] / 120
        avg_z = accel['yaw'] / 120

        # convert acceleration to velocity
        x = (avg_x - base_x) ** 2
        y = (avg_y - base_y) ** 2
        z = (avg_z - base_z) ** 2
        # compute velocity and raise base value
        self._accel = math.sqrt(x + y + z) * 20
        return str(self._accel).split(".")[0]

    def display_accel(self):
        # since we can't directly dictate the length SenseHat reads
        # accelerometer sensors, the following will help provide
        # enough time for the students to initiate movement
        self.sense_hat.clear(Iot.DisplayColors.RED.value)
        sleep(1)
        self.sense_hat.clear(Iot.DisplayColors.YELLOW.value)
        sleep(1)
        self.sense_hat.clear(Iot.DisplayColors.GREEN.value)
        sleep(1)
        self.sense_hat.show_message(str(self._accel), text_colour=Iot.DisplayColors.BLUE.value, scroll_speed=0.02)
        logging.info('Display Acceleration Success')

    def display_accel_brake(self):
        # we can't acutally simulate brakes without having continual 
        # accel being calculated. This is just a visual representation.
        phase = ImageMaps['phase']

        for i in range(3):
            self.sense_hat.set_pixels(phase[0])
            sleep(.5)
            self.sense_hat.set_pixels(phase[1])
            sleep(.5)
        self.sense_hat.clear(Iot.DisplayColors.RED.value)

    def accel_critical(self):
        # called when accel is registered over 100mph
        wrn_img = ImageMaps['alerts'][0]
        alt_img = ImageMaps['faces'][0]

        for i in range(3):
            self.sense_hat.set_pixels(wrn_img)
            sleep(.5)
            self.sense_hat.show_message('DANGER!', text_colour=Iot.DisplayColors.RED.value, scroll_speed=.03)
            self.sense_hat.set_pixels(alt_img)
            sleep(.5)
        self.sense_hat.clear()

    def display_color(self, color):
        if color:
            check_color = Iot.DisplayColors.get(color.upper())
            if check_color:
                self.sense_hat.clear(check_color)
                if color == 'GREEN':
                    return self.secrets.CURIOUS.value
                return color
        return f'Invalid color: {color}'

    @property
    def get_heartrate(self):
        heartrate = random.randint(60, 110)
        self._heartrate_val = f'{heartrate} bpm'
        return self._heartrate_val

    def display_heartrate(self, heartrate):
        print(f'Getting heartrate for the next 3 seconds...')

        # get image maps
        heart_maps = ImageMaps['heart']
        hr_maps = ImageMaps['heartrate']
         
        # display heart map
        self.sense_hat.set_pixels(heart_maps[0])
        sleep(1)
        self.sense_hat.clear()

        # display heartrate maps
        for hr_map in hr_maps:
            self.sense_hat.set_pixels(hr_map)
            sleep(.1)
        
        # display heartrate
        self.sense_hat.show_message(str(heartrate), scroll_speed=0.2)
        self.sense_hat.clear()

    def heart_critical(self):
        wrn_img = ImageMaps['alerts'][0]
        alt_img = ImageMaps['faces'][0]
        steve = ImageMaps['faces'][2]

        for i in range(3):
            self.sense_hat.set_pixels(wrn_img)
            sleep(.5)
            self.sense_hat.show_message('PATIENT CRITICAL!', text_colour=Iot.DisplayColors.RED.value, scroll_speed=.03)
            self.sense_hat.set_pixels(alt_img)
            sleep(.5)
        self.sense_hat.set_pixels(steve)
        sleep(.5)
        self.sense_hat.clear()

    @property
    def get_temp(self):
        temp = round((self.sense_hat.get_temperature() * (9/5) + 32), 2)
        self._temp = f'{temp}f'
        return self._temp

    def display_temp(self):
        self.sense_hat.show_message(str(self._temp), text_colour=Iot.DisplayColors.BLUE.value, scroll_speed=0.2)
        logging.info('Display temperature success')
   
    @property
    def get_humidity(self):
        humidity = round(self.sense_hat.get_humidity(), 2)
        self._humidity = f'{humidity}%'
        return self._humidity

    def display_humidity(self):
        self.sense_hat.show_message(str(self._humidity), text_colour=Iot.DisplayColors.GREEN.value, scroll_speed=0.2)
        logging.info('Success')

    @property
    def get_pressure(self):
        pressure = round(self.sense_hat.get_pressure(), 2)
        self._pressure = f'{pressure} mbar'
        return self._pressure

    def display_pressure(self):
        self.sense_hat.show_message(str(self._pressure), text_colour=Iot.DisplayColors.RED.value, scroll_speed=0.2)
        logging.info('Success')

    @property
    def get_combination(self):
        return self.combination_str
    
    def display_combination(self):
        # Displays lock combination via Morse code
        combination = self.combination_str
        
        # dits are 0.09 seconds; dahs are 1 second
        for val in combination:
            for pos in val:
                if pos == '.':
                    self.sense_hat.clear(255, 0, 0)
                    sleep(0.09)
                    self.sense_hat.clear()
                else:
                    self.sense_hat.clear(255, 0, 0)
                    sleep(0.8)
                    self.sense_hat.clear()
                sleep(0.9)
            sleep(1)

        message = 'Combination complete; Cleaning up...'
        self.sense_hat.clear()
        logging.info(message)

    def display_ssn(self):
        locks = ImageMaps['lock']
        self.sense_hat.set_pixels(locks[0])
        sleep(.5)
        self.sense_hat.set_pixels(locks[1])
        sleep(1)
        self.sense_hat.set_pixels(locks[0])
        sleep(.5)
        self.sense_hat.set_pixels(locks[1])

    def get_patients(self):
        with open(Files.Data.patients, 'r') as f:
            ssn_json = json.load(f)
        return ssn_json

    def radio(self, new_station):
        msg = f'Now Playing: {new_station}'
        self.sense_hat.show_message(text_string=msg, text_colour=Iot.DisplayColors.PURPLE.value, scroll_speed=0.5)
        return new_station

    def get_radio(self):
        with open(Files.Data.stations, 'r') as f:
            stations = json.load(f)
        return str(random.choice(stations))

    def vehicle(self):
        logo = ImageMaps['logo']
        self.sense_hat.set_pixels(logo[1])

    def get_vehicle(self):
        return TeslaIoT().get_vehicle()

    def car_user(self):
        logo = ImageMaps['logo']
        self.sense_hat.set_pixels(logo[0])

    def get_user(self):
        return TeslaIoT().user()

    def products(self):
        logo = ImageMaps['logo']
        self.sense_hat.set_pixels(logo[1])

    def get_products(self):
        return TeslaIoT().user()

    def trip_planner(self):
        logo = ImageMaps['logo']
        self.sense_hat.set_pixels(logo[2])

    def get_trip(self):
        return TeslaIoT().user()

    def list_commands(self):
        f = Iot.Commands()
        commands = dict((cmd, getattr(f, cmd)) for cmd in dir(Iot.Commands) if not cmd.startswith('__'))
        colors = Iot.DisplayColors.to_dict()
        return {'commands': commands, 'colors': Iot.DisplayColors.to_dict()}

    def connected(self):
        """
            Displays a rotating TV img. Used to visually
            notify a successful connection to the MQTT
            server
        """
        G = (192, 192, 192)
        B = (0, 0, 128)
        C = (255, 255, 1)
        K = (100, 100, 100)

        img = [
                B, B, B, B, B, B, B, B,
                B, B, G, B, B, G, B, B,
                B, B, B, G, G, B, B, B,
                B, B, C, C, C, C, B, B,
                B, B, C, K, K, C, B, B,
                B, B, C, K, K, C, B, B,
                B, B, C, C, C, C, B, B,
                B, B, B, B, B, B, B, B,
                ]
        self.sense_hat.set_pixels(img)
        r = [0, 90, 180, 270]
        for i in range(2):
            for rot in r:
                self.sense_hat.set_rotation(rot)
                sleep(.5)

        self.sense_hat.set_rotation(0)
        self.sense_hat.clear()
    
    def display_message(self, message):
        self.sense_hat.show_message(str(message), scroll_speed=0.2)
    
    def snake(self):
        os.system('./snake')

    def get_all_sensor_data(self):
        """
            Collects and returns all SenseHat sensory data as a dict
        """
        current_time = int(time())
        system_data = self.system_info
        
        if current_time - self.sys_time > 300:
            system_data = SystemInfo().get_all_info()
        print(f'system_data: {system_data}')
        # get device orientation in degrees
        orientation = self.sense_hat.get_orientation()
        sense_return_dict = {
            "ts": current_time,
            "sensor_data": {
                "temp": self.get_temp,
                "humidity": self.get_humidity,
                "pressure": self.get_pressure,
                "x": round(orientation['pitch'], 2),
                "y": round(orientation['roll'], 2),
                "z": round(orientation['yaw'], 2),
                "heart": self.get_heartrate,
                "flag": '',
                'color': '',
                'car': {
                    'vehicle': '',
                    'trip': '',
                    'products': '',
                    'user': '',
                },
                'patients': ''
            },
            "system": system_data,
        }
        return sense_return_dict

# [ eof ]
