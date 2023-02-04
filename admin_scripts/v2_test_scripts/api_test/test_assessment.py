import os
import time
import requests
import psutil


def check_cpu_usage():
    current_cpu_percent = psutil.cpu_percent(interval=1)
    if current_cpu_percent >= 40.0:
        return True
    else:
        return False


def assess_publish():
    url = os.environ.get(f"URL")
    q0_key = os.environ.get(f'Q0_KEY')
    build_id = os.environ.get('BUILD_ID')

    data = {
        "question_id": q0_key,
    }

    response = requests.put(f"{url}{build_id}", json=data)
    print(response)


last_reboot = psutil.boot_time()
current_time = time.time()

if current_time - last_reboot > 300:
    assess_publish()
    if check_cpu_usage():
        assess_publish()
        print("Workout Complete")
    else:
        print("Incomplete")
