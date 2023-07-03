import requests
from urllib.parse import urljoin


DEFAULT_URL = "http://localhost:8080"


def test_assessment():
    url = input(f"What URL would you like to test? [{DEFAULT_URL}] ") or DEFAULT_URL
    build_id = input("Which build ID would you like to test? ")
    question_key = input(f"What is the question ID you would like to test? ")
    data = {"question_key": question_key}
    full_url = urljoin(url, f"api/unit/workout/{build_id}")
    resp = requests.put(full_url, json=data)
    print(resp.status_code)


if __name__ == '__main__':
    test_assessment()
