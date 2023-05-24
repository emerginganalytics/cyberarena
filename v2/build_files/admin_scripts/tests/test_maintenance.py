from handlers.maintenance_handler import MaintenanceHandler
from cloud_fn_utilities.periodic_maintenance.daily_maintenance import DailyMaintenance
from cloud_fn_utilities.periodic_maintenance.hourly_maintenance import HourlyMaintenance
from cloud_fn_utilities.periodic_maintenance.quarter_hourly_maintenance import QuarterHourlyMaintenance


__author__ = "Philip Huff"
__copyright__ = "Copyright 2023, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Production"


if __name__ == "__main__":
    response = str(input(f"Do you want to test the Maintenance Handler function itself? [Y/n] "))
    if not response.upper().startswith("N"):
        MaintenanceHandler().route()

    response = str(input(f"What type of Maintenance do you want to run? ([D]aily, [H]ourly, [Q]uarter-hourly) "))
    if str.upper(response).startswith("D"):
        DailyMaintenance(debug=True).run()
    elif str.upper(response).startswith("H"):
        HourlyMaintenance(debug=True).run()
    elif str.upper(response).startswith("Q"):
        QuarterHourlyMaintenance(debug=True).run()
