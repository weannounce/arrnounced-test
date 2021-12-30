from flask import Flask, request, jsonify
import requests
import sys
import threading
from datetime import datetime


rx_lists = {}
tx_lists = {}
tx_dicts = {}


class Backend:
    def __init__(self, name, apikey, port=None):
        self.name = name
        self.apikey = apikey
        self.thread = None

        if port is not None:
            self.port = port
        elif "sonarr" in name.lower():
            self.port = 8989
        elif "radarr" in name.lower():
            self.port = 7878
        elif "lidarr" in name.lower():
            self.port = 8686
        else:
            print("Not backend port specified!")
            sys.exit(1)


_backends = {}


def get_date_diff(release, publish_date):
    dt = datetime.strptime(publish_date, "%Y-%m-%dT%H:%M:%S.%f")
    return abs((release.announce_time - dt).total_seconds())


def check_first_rx(test_suite, backend, release):
    test_suite.assertNotEqual(
        len(rx_lists[backend.name]), 0, "No announcements to this backend"
    )
    rx = rx_lists[backend.name].pop(0)
    _check_rx(test_suite, backend, rx, release)


def find_and_check_rx(test_suite, backend, release):
    test_suite.assertNotEqual(
        len(rx_lists[backend.name]), 0, "No announcements to this backend"
    )
    rx = next(
        filter(lambda x: x["title"] == release.title, rx_lists[backend.name]), None
    )
    test_suite.assertNotEqual(rx, None, "Backend did not receive release")

    rx_lists[backend.name].remove(rx)
    _check_rx(test_suite, backend, rx, release)


def _check_rx(test_suite, backend, rx, release):
    local_indexer = None
    if "lidarr" not in backend.name.lower():
        local_indexer = "Irc" + release.indexer
    test_suite.assertEqual(release.title, rx["title"], "Title is not matching")
    test_suite.assertEqual(
        release.url, rx["downloadUrl"], "Download URL is not matching"
    )
    test_suite.assertEqual(local_indexer, rx.get("indexer"), "Indexer is not matching")
    test_suite.assertTrue(
        get_date_diff(release, rx["publishDate"]) < 1, "Publish date is too old"
    )
    test_suite.assertEqual(release.protocol, rx["protocol"], "Protocol is not matching")
    test_suite.assertEqual(backend.apikey, rx["apikey"], "API key is not matching")


def max_announcements(test_suite, name, nr):
    for _ in range(nr):
        received(name)
    test_suite.assertEqual(received(name), None)


def received(name):
    return None if len(rx_lists[name]) == 0 else rx_lists[name].pop(0)


def send(name, response):
    tx_lists[name].append(response)


def send_approved(name, approved):
    tx_lists[name].append({"approved": approved})


def send_approved_title(name, release, approved):
    tx_dicts[name][release.title] = {"approved": approved}


def clear_all_backends():
    for b in rx_lists.keys():
        rx_lists[b] = []
    for b in tx_lists.keys():
        tx_lists[b] = []
    for b in tx_dicts.keys():
        tx_dicts[b] = {}


def get_tx_list(backend_name):
    return tx_lists[backend_name]


def get_tx_dict(backend_name):
    return tx_dicts[backend_name]


def get_rx_list(backend_name):
    return rx_lists[backend_name]


push_done = threading.Event()
push_counter = 0


def _approved(something):
    return (
        isinstance(something, dict)
        and "approved" in something
        and something["approved"] is True
    )


# TODO: Check API key
def _run_backend(backend):  # noqa: C901
    app = Flask(backend.name)

    def _push():
        global push_counter
        rx_list = get_rx_list(backend.name)
        tx_list = get_tx_list(backend.name)
        tx_dict = get_tx_dict(backend.name)

        rx_list.append(request.json)
        rx_list[-1]["apikey"] = request.headers["X-Api-Key"]

        if len(tx_list) != 0:
            ret = tx_list.pop(0)
        elif request.json["title"] in tx_dict:
            ret = tx_dict.pop(request.json["title"])
        else:
            ret = {"approved": False}

        print(backend.name, "got", rx_list[-1]["title"], ":", ret)
        push_counter -= 1
        # Notify test thread that push is completed if the release is approved
        # or pushed to all backends.
        if _approved(ret) or push_counter <= 0:
            push_counter = len(_backends)
            push_done.set()
        return jsonify(ret)

    @app.route("/api/release/push", methods=["POST"])
    def push():
        return _push()

    @app.route("/api/v1/release/push", methods=["POST"])
    def push_v1():
        return _push()

    @app.route("/api/v3/release/push", methods=["POST"])
    def push_v3():
        return _push()

    @app.route("/api/diskspace", methods=["GET"])
    def diskspace():
        return jsonify({})

    @app.route("/api/v1/diskspace", methods=["GET"])
    def diskspace_v1():
        return jsonify({})

    @app.route("/api/v3/diskspace", methods=["GET"])
    def diskspace_v3():
        return jsonify({})

    @app.route("/shutdown")
    def shutdown():
        func = request.environ.get("werkzeug.server.shutdown")
        if func is None:
            raise RuntimeError("Not running with the Werkzeug Server")
        func()
        return "Shutting down..."

    app.run(port=backend.port)


def _call_shutdown(port):
    return requests.get(f"http://localhost:{port}/shutdown").status_code == 200


def stop():
    global _backends
    global rx_lists
    global tx_lists
    global tx_dicts
    global push_done
    global push_counter
    for b in _backends.keys():
        if _backends[b].thread is not None:
            if not _call_shutdown(_backends[b].port):
                print("Could not shutdown " + _backends[b].name)
            _backends[b].thread.join()
            _backends[b].thread = None

    _backends = {}
    rx_lists = {}
    tx_lists = {}
    tx_dicts = {}
    push_done.clear()
    push_counter = len(_backends)


def _create_thread(backend):
    backend.thread = threading.Thread(
        target=_run_backend,
        args=(backend,),
    )
    backend.thread.start()


def run(config):
    global _backends
    for backend in config.backends.values():
        rx_lists[backend.name] = []
        tx_lists[backend.name] = []
        tx_dicts[backend.name] = {}
        _create_thread(backend)
    _backends = config.backends
