import requests

session = None


def login(config):
    global session
    session = requests.Session()
    result = session.post(
        f"http://localhost:{config.web_port}/login",
        data={"username": config.web_username, "password": config.web_password},
    )
    if result.status_code != 200:
        print("Login failed")


def logout():
    global session
    session = None


def renotify(test_suite, config, announcement, backend_name):
    result = session.post(
        f"http://localhost:{config.web_port}/notify",
        json={"id": announcement.id, "backend_name": backend_name},
    )

    test_suite.assertEqual(result.status_code, 200)
