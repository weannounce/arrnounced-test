from flask import Flask, request, jsonify
import requests
import threading

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

backends = { "sonarr": Backend("sonarr", 8989),
        "radarr": Backend("radarr", 7878),
        "lidarr": Backend("lidarr", 8686)}


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


def _run_backend(name, port, rx_list, tx_list):
    app = Flask(name)

    @app.route('/api/release/push', methods=['POST'])
    def push():
        rx_list.append(request.json)

        if len(tx_list) == 0:
            return jsonify({"approved": False})
        else:
            return jsonify(tx_list.pop(0))

    @app.route('/api/v1/release/push', methods=['POST'])
    def push_v1():
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


def _create_thread(backend, rx_list, tx_list):
    backend.thread = threading.Thread(target=_run_backend,
            args=(backend.name, backend.port, rx_list, tx_list))
    backend.thread.start()


def run(sonarr=True, radarr=True, lidarr=True):
    global backends
    if sonarr:
        _create_thread(backends["sonarr"], sonarr_rx, sonarr_tx)

    if radarr:
        _create_thread(backends["radarr"], radarr_rx, radarr_tx)

    if lidarr:
        _create_thread(backends["lidarr"], lidarr_rx, lidarr_tx)
