from flask import Flask, request, jsonify
import threading
import time
sonarr_rx = []
radarr_rx = []
lidarr_rx = []

sonarr_tx = []
radarr_tx = []
lidarr_tx = []

def sonarr_send(approved):
    sonarr_tx.append(approved)
def radarr_send(approved):
    radarr_tx.append(approved)
def lidarr_send(approved):
    lidarr_tx.append(approved)

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


def run_backend(name, port, rx_list, tx_list):
    app = Flask(name)

    @app.route('/api/release/push', methods=['POST'])
    def push():
        rx_list.append(request.json)

        if len(tx_list) == 0:
            return jsonify({"approved": False})
        else:
            return jsonify({"approved": tx_list.pop(0)})

    @app.route('/api/v1/release/push', methods=['POST'])
    def push_v1():
        rx_list.append(request.json)

        if len(tx_list) == 0:
            return jsonify({"approved": False})
        else:
            return jsonify({"approved": tx_list.pop(0)})

    @app.route('/')
    def hello_world():
        print(request.json)
        return "Hello world!"

    app.run(port=port)

def run_backends():
    sonarr_thread = threading.Thread(target=run_backend, args=("sonarr", 8989, sonarr_rx, sonarr_tx))
    sonarr_thread.start()

    radarr_thread = threading.Thread(target=run_backend, args=("radarr", 7878, radarr_rx, radarr_tx))
    radarr_thread.start()

    lidarr_thread = threading.Thread(target=run_backend, args=("lidarr", 8686, lidarr_rx, lidarr_tx))
    lidarr_thread.start()

#lidarr_send(False)
#lidarr_send(True)
#
#while True:
#    time.sleep(10)
#    if 0 != len(sonarr_rx):
#        print("sonarr: ", sonarr_rx)
#        sonarr_rx = []
#    if 0 != len(radarr_rx):
#        print("radarr: ", radarr_rx)
#        radarr_rx = []
#    if 0 != len(lidarr_rx):
#        print("lidarr: ", lidarr_rx)
#        lidarr_rx = []
