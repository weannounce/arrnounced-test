from flask import Flask, request, jsonify
import requests
import threading
from  datetime import datetime
from enum import Enum

class BackendType(Enum):
    SONARR = 1
    RADARR = 2
    LIDARR = 3

sonarr_rx = []
radarr_rx = []
lidarr_rx = []

sonarr_tx = []
radarr_tx = []
lidarr_tx = []

class Backend:
    def __init__(self, name, port):
        self.name = name
        self.port = port
        self.thread = None

backends = { BackendType.SONARR: Backend("sonarr", 8989),
        BackendType.RADARR: Backend("radarr", 7878),
        BackendType.LIDARR: Backend("lidarr", 8686)}

def get_date_diff(publish_date):
    now = datetime.now()
    dt = datetime.strptime(publish_date, "%Y-%m-%dT%H:%M:%S.%f")
    return (now - dt).total_seconds()

def check_sonarr_rx(test_suite, title, dlUrl, indexer, protocol="Torrent"):
    _check_rx(sonarr_rx, test_suite, title, dlUrl, indexer, protocol)
def check_radarr_rx(test_suite, title, dlUrl, indexer, protocol="Torrent"):
    _check_rx(radarr_rx, test_suite, title, dlUrl, indexer, protocol)
def check_lidarr_rx(test_suite, title, dlUrl, protocol="Torrent"):
    _check_rx(lidarr_rx, test_suite, title, dlUrl, None, protocol)

def _check_rx(rx_list, test_suite, title, dlUrl, indexer, protocol):
    test_suite.assertNotEqual(len(rx_list),0)
    rx = rx_list.pop(0)

    if indexer is not None:
        indexer = "Irc" + indexer
    test_suite.assertEqual(title, rx["title"], "Title is not matching")
    test_suite.assertEqual(dlUrl, rx["downloadUrl"], "Download URL is not matching")
    test_suite.assertEqual(indexer, rx.get("indexer"), "Indexer is not matching")
    test_suite.assertTrue(get_date_diff(rx["publishDate"]) < 5, "Publish date is too old")
    test_suite.assertEqual(protocol, rx["protocol"], "Protocol is not matching")

def sonarr_max_announcements(test_suite, nr):
    for i in range(nr):
        sonarr_received()
    test_suite.assertEqual(sonarr_received(), None)
def radarr_max_announcements(test_suite, nr):
    for i in range(nr):
        radarr_received()
    test_suite.assertEqual(radarr_received(), None)
def lidarr_max_announcements(test_suite, nr):
    for i in range(nr):
        lidarr_received()
    test_suite.assertEqual(lidarr_received(), None)

def sonarr_received():
    return None if len(sonarr_rx) == 0 else sonarr_rx.pop(0)
def radarr_received():
    return None if len(radarr_rx) == 0 else radarr_rx.pop(0)
def lidarr_received():
    return None if len(lidarr_rx) == 0 else lidarr_rx.pop(0)

def sonarr_send(response):
    sonarr_tx.append(response)
def radarr_send(response):
    radarr_tx.append(response)
def lidarr_send(response):
    lidarr_tx.append(response)

def sonarr_send_approved(approved):
    sonarr_tx.append({"approved": approved})
def radarr_send_approved(approved):
    radarr_tx.append({"approved": approved})
def lidarr_send_approved(approved):
    lidarr_tx.append({"approved": approved})

def clear_all_backends():
    global sonarr_rx
    global radarr_rx
    global lidarr_rx
    global sonarr_tx
    global radarr_tx
    global lidarr_tx

    sonarr_rx = []
    radarr_rx = []
    lidarr_rx = []

    sonarr_tx = []
    radarr_tx = []
    lidarr_tx = []

def get_tx_list(backend_type):
    if backend_type == BackendType.SONARR:
        return sonarr_tx
    if backend_type == BackendType.RADARR:
        return radarr_tx
    if backend_type == BackendType.LIDARR:
        return lidarr_tx

def get_rx_list(backend_type):
    if backend_type == BackendType.SONARR:
        return sonarr_rx
    if backend_type == BackendType.RADARR:
        return radarr_rx
    if backend_type == BackendType.LIDARR:
        return lidarr_rx

def _run_backend(name, port, backend_type):
    app = Flask(name)

    @app.route('/api/release/push', methods=['POST'])
    def push():
        rx_list = get_rx_list(backend_type)
        tx_list = get_tx_list(backend_type)

        rx_list.append(request.json)

        if len(tx_list) == 0:
            return jsonify({"approved": False})
        else:
            return jsonify(tx_list.pop(0))

    @app.route('/api/v1/release/push', methods=['POST'])
    def push_v1():
        rx_list = get_rx_list(backend_type)
        tx_list = get_tx_list(backend_type)

        rx_list.append(request.json)

        if len(tx_list) == 0:
            return jsonify({"approved": False})
        else:
            return jsonify(tx_list.pop(0))

    @app.route('/shutdown')
    def shutdown():
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        func()
        return "Shutting down..."

    app.run(port=port)


def _call_shutdown(port):
    return requests.get("http://localhost:{}/shutdown".format(port)).status_code == 200


def stop():
    global backends
    for b in backends.keys():
        if backends[b].thread is not None:
            if not _call_shutdown(backends[b].port):
                print("Could not shutdown " + backends[b].name)
            backends[b].thread.join()
            backends[b].thread = None


def _create_thread(backend_type):
    global backends
    backends[backend_type].thread = threading.Thread(target=_run_backend,
            args=(backends[backend_type].name, backends[backend_type].port, backend_type))
    backends[backend_type].thread.start()


def run(sonarr=True, radarr=True, lidarr=True):
    if sonarr:
        _create_thread(BackendType.SONARR)

    if radarr:
        _create_thread(BackendType.RADARR)

    if lidarr:
        _create_thread(BackendType.LIDARR)
