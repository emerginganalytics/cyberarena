import requests
import os
import json


def send(question_key, build_id, url):
    URL = f'http://cyberarena.ncta-pd.org/api/unit/workout/lqzwpuiovt'
    data = {"question_key": question_key}
    resp = requests.put(URL, json=data)
    print(resp.status_code)


if __name__ == '__main__':
    question_key = 1177
    build_id = 'lqzwpuiovt'
    url = 'localhost:5000/api/unit/workout/'
    send(question_key, build_id, url)
