import requests

session = None


def login(config):
    global session
    session = requests.Session()
    result = session.post(
        "http://localhost:{}/login".format(config.web_port),
        data={"username": config.web_username, "password": config.web_password},
    )
    if result.status_code != 200:
        print("Login failed")


def logout():
    global session
    session = None


def renotify(test_suite, config, announcement, backend_id):
    result = session.post(
        "http://localhost:{}/notify".format(config.web_port),
        json={"id": announcement.id, "backend_id": backend_id},
    )

    test_suite.assertEqual(result.status_code, 200)
