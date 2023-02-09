from cloud_fn_utilities.periodic_maintenance.daily_maintenance import DailyMaintenance


__author__ = "Philip Huff"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Production"


class TestDailyMaintenance:
    def __init__(self):
        self.daily_maintenance = DailyMaintenance()

    def run(self):
        self.daily_maintenance.run()


if __name__ == "__main__":
    TestDailyMaintenance().run()
