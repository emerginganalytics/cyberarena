from google.cloud import runtimeconfig
import pymysql
import itertools


class IOTDatabase:
    """
    This class abstracts the interaction with the IoT MySQL database table.
    A copy of the class in cybergym.cloud_functions.common.database
    Usage:
        iotdb = IOTDatabase()
        iotdb.update_rpi_sense_hat_data(device_num_id, ts, sensor_data, memory, ip, storage)
        # Or use this when retrieving data
        iot_data = iotdb.get_rpi_sense_hat_data(device_num_id)
        json_data = json.load(iot_data['sensor_data'])
    """
    RPI_SENSE_HAT = "rpi_sense_hat"

    def __init__(self):
        runtimeconfig_client = runtimeconfig.Client()
        myconfig = runtimeconfig_client.config('cybergym')
        mysql_password = myconfig.get_variable('sql_password').value.decode("utf-8")
        mysql_ip = myconfig.get_variable('sql_ip').value.decode("utf-8")
        print('Connecting to db at %s' % mysql_ip)
        self.dbcon = pymysql.connect(host=mysql_ip,
                                     user="root",
                                     password=mysql_password,
                                     db='cybergym',
                                     charset='utf8mb4')

    def get_rpi_sense_hat_data(self, device_num_id):
        """
        Gets the realtime data from the IoT database table for the given device_num_id
        @param device_num_id: key for the device
        @type device_num_id: Integer
        @return: The full row for the requested device or None if no row exists for the device_num_id
        @rtype: Dict or None
        """
        dbcur = self.dbcon.cursor()
        iot_select = f"""
                        SELECT *
                        FROM {self.RPI_SENSE_HAT}
                        WHERE device_num_id = %s
                        """
        iot_args = (device_num_id)
        dbcur.execute(iot_select, iot_args)
        row = dbcur.fetchone()
        if not row:
            return None
        desc = dbcur.description
        column_names = [col[0] for col in desc]
        iot_data = dict(itertools.zip_longest(column_names, row))
        dbcur.close()
        return iot_data
