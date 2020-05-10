import requests
from . import config as global_config

session = None


def login(config):
    global session
    session = requests.Session()
    result = session.post(
        "http://localhost:{}/login".format(config.web_port),
        data={
            "username": global_config.web_username,
            "password": global_config.web_password,
        },
    )
    if result.status_code != 200:
        print("Login failed")


def logout():
    global session
    session = None


def renotify(test_suite, config, announcement, backend_name):
    result = session.post(
        "http://localhost:{}/notify".format(config.web_port),
        json={"id": announcement.id, "backend_name": backend_name},
    )

    test_suite.assertEqual(result.status_code, 200)
