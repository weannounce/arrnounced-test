import requests
import subprocess
import os
from helpers import config

container_name = "arrnounced_test"
current_directory = os.getcwd()
timezone = os.path.realpath("/etc/localtime")

arr_process = None


def stop():
    global arr_process
    print("Stopping Arrnounced")

    if requests.get("http://localhost:3467/shutdown").status_code != 200:
        print("Failed to shutdown Arrnounced. Killing instead!")
        if config.docker is None:
            arr_process.kill()
        else:
            subprocess.Popen(["docker", "container", "stop", container_name]).wait()
    else:
        arr_process.wait()


def run():
    global arr_process
    if config.docker is None:
        print("Starting Arrnounced from source")
        arr_process = subprocess.Popen(
            [
                "coverage",
                "run",
                "-p",
                "--source",
                "../arrnounced/src",
                "../arrnounced/src/arrnounced.py",
                "-v",
                "-c",
                "data/settings.cfg",
                "-d",
                "data",
                "-t",
                "trackers",
            ]
        )
    else:
        print("Starting Arrnounced docker container")
        arr_process = subprocess.Popen(
            [
                "docker",
                "run",
                "--name",
                container_name,
                "--rm",
                "--net=host",
                "--user",
                str(os.getuid()),
                "-v",
                current_directory + "/data:/config",
                "-v",
                current_directory + "/trackers:/trackers",
                "-e",
                "TZ=" + timezone,
                "-e",
                "VERBOSE=Y",
                "weannounce/arrnounced:" + config.docker,
            ]
        )
