from datetime import datetime, timedelta, timezone


def datetime_local_to_utc_ts(dt_str):
    local_ts = datetime.strptime(dt_str, "%Y-%m-%dT%H:%M").timestamp()
    return datetime.utcfromtimestamp(local_ts).timestamp()
