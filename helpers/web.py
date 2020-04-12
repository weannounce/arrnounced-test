import requests
from . import config

session = None
def login():
    global session
    session = requests.Session()
    result = session.post("http://localhost:{}/login".format(config.arrnounced_port),
             data={"username": config.web_username, "password": config.web_password})
    if result.status_code != 200:
        print("Login failed")

def logout():
    global session
    session = None

def renotify(test_suite, announcement, backend_name):
    result = session.post("http://localhost:{}/notify".format(config.arrnounced_port),
             json={"id": announcement.id, "backend_name": backend_name})

    test_suite.assertEqual(result.status_code, 200)
