# Old Cloud Function
```python
def cloud_fn_iot_capture_sensor(event, context):
    """
        Listens on IOT PubSub topic and updates and forwards data from a SQL database to the Classified Cloud Run
        application.
    """
    if not bm.check_budget():
        cloud_log(LogIDs.BUDGET_MANAGEMENT, "BUDGET ALERT: Cannot run cloud_fn_iot_capture_sensor because the budget "
                                            "exceeded variable is set for the project", LOG_LEVELS.ERROR)
        return
    my_function_name = "cloud_fn_iot_capture_sensor"
    device_num_id = Utilities.check_variable(event['attributes'], 'deviceNumId', my_function_name, LogIDs.IOT)
    sensor_data = Utilities.check_variable(event, 'data', my_function_name, LogIDs.IOT)
    event_data = json.loads(base64.b64decode(sensor_data).decode('UTF-8'))

    system_data = event_data.get('system', None)
    memory = ip = storage = None

    print(event)
    print(f'telemetry data: {event_data}')
    if system_data:
        memory = system_data.get('memory', None)
        ip = system_data.get('ip', None)
        storage = system_data.get('storage', None)

    iotdb = IOTDatabase()
    try:
        iotdb.update_rpi_sense_hat_data(device_num_id=device_num_id,
                                        ts=event_data['ts'],
                                        sensor_data=json.dumps(event_data['sensor_data']),
                                        memory=memory,
                                        ip=ip,
                                        storage=storage)
    except KeyError as err:
        cloud_log(LogIDs.IOT, f"Key error: '{err.args[0]}' not found", LOG_LEVELS.ERROR)
    except:
        cloud_log(LogIDs.IOT, f"Unspecified error when updating IoT", LOG_LEVELS.ERROR)
```

# Current Device Return Object
```python
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
```
# Stored Datastore Object
```python
device_ds = {
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
    },
    'car': {
        'vehicle': '',
        'trip': '',
        'products': '',
        'user': '',
    },
    'patients': {...},
    "system": system_data,
}
```

