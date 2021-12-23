from google.cloud import runtimeconfig
from common.globals import cloud_log, LogIDs, LOG_LEVELS
import pymysql
import itertools


class IOTDatabase:
    """
    This class abstracts the interaction with the IoT MySQL database table.
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
        return iot_data


    def update_rpi_sense_hat_data(self, device_num_id, ts, sensor_data, memory=None, ip=None, storage=None):
        """
        Performs a database upsert for the given device_num_id. It will delete the current row for device_num_id,
        and insert a row with the given data.
        @param device_num_id: Primary key for the database
        @type device_num_id: String
        @param ts: Timestamp from the IoT device
        @type ts: String
        @param sensor_data: json data from the IoT device
        @type sensor_data: String
        @param memory: The amount of memory in the IoT device
        @type memory: String
        @param ip: Current IP address of the IoT device
        @type ip: String
        @param storage: Remaining storage in the IoT device
        @type storage: String
        @return: None
        """
        dbcur = self.dbcon.cursor()
        iot_upsert = f"""
                        REPLACE INTO {self.RPI_SENSE_HAT}
                            (device_num_id, ts, sensor_data, memory, ip, storage)
                        VALUES 
                            (%s, %s, %s, %s, %s, %s)
                        """
        iot_args = (device_num_id, ts, sensor_data, memory, ip, storage)

        try:
            return_value = dbcur.execute(iot_upsert, iot_args)
        except pymysql.err.ProgrammingError as ex:
            # If the table does not exist, then create it first.
            if self._create_rpi_sense_hat_database():
                dbcur.execute(iot_upsert, iot_args)
            else:
                cloud_log(LogIDs.IOT, "Unknown error: Could not create table for IoT.", LOG_LEVELS.ERROR)
        finally:
            self.dbcon.commit()
            self.dbcon.close()
        return return_value

    def _create_rpi_sense_hat_database(self):
        """
        Sets up the database for storing Raspberry PI SenseHat data.
        :returns: True if the database needed to set up and otherwise False
        """
        dbcur = self.dbcon.cursor()
        dbcur.execute(f"""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_name = '{self.RPI_SENSE_HAT}'
            """)
        if dbcur.fetchone()[0] == 1:
            dbcur.close()
            return False

        dbcur.execute(f"""
            CREATE TABLE {self.RPI_SENSE_HAT}(
                device_num_id varchar(255) primary key,
                ts varchar(255),
                sensor_data varchar(10000),
                memory varchar(255),
                ip varchar(255),
                storage varchar(255)
                )
        """)
        dbcur.close()
        return True
