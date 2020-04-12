import requests
from . import config

cookie_jar = None
session = None
def login():
    global cookie_jar
    global session
    session = requests.Session()
    result = session.post("http://localhost:{}/login".format(config.arrnounced_port),
             data={"username": config.web_username, "password": config.web_password})
    if result.status_code != 200:
        print("anot 23000")
    cookie_jar = result.cookies
    #print(cookie_jar["session"])

def renotify(test_suite, announcement, backend_name):
    result = session.post("http://localhost:{}/notify".format(config.arrnounced_port),
             json={"id": announcement.id, "backend_name": backend_name},
             cookies=cookie_jar)

    test_suite.assertEqual(result.status_code, 200)
