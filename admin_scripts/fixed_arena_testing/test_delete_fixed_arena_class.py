from cloud_fn_utilities.periodic_maintenance.hourly_maintenance import HourlyMaintenance


__author__ = "Philip Huff"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Production"


class TestFixedArenaDelete:
    def __init__(self):
        pass

    def run(self):
        HourlyMaintenance(debug=True).delete_expired()


if __name__ == "__main__":
    TestFixedArenaDelete().run()
