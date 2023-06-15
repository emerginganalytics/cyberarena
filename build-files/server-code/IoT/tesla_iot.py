import json
from globals import Configuration, Files, Iot


class TeslaIoT:
    class DataKeys:
        VEHICLE = 'vehicle'
        USER = 'user'
        PRODUCTS = 'products'
        TRIP_PLANNER = 'trip_planner'

    def __init__(self):
        self.data_file = Files.Data.car
        self.json_data = self.load_file()

    def load_file(self):
        with open(self.data_file, 'r') as f:
            data = json.load(f)
        return data

    def get_vehicle(self):
        return self.json_data.get(self.DataKeys.VEHICLE, None)

    def user(self):
        return self.json_data.get(self.DataKeys.USER, None)

    def product(self):
        return self.json_data.get(self.DataKeys.PRODUCTS, None)

    def trip_planner(self):
        return self.json_data.get(self.DataKeys.TRIP_PLANNER, None)
