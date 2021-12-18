import requests
import subprocess
import os
import shutil
from helpers import config as global_config

container_name = "arrnounced_test"
current_directory = os.getcwd()
timezone = os.path.realpath("/etc/localtime")

arr_process = None


def stop(config):
    global arr_process
    print("Stopping Arrnounced")

    if (
        requests.get("http://localhost:{}/shutdown".format(config.web_port)).status_code
        != 200
    ):
        print("Failed to shutdown Arrnounced. Killing instead!")
        if global_config.docker is None:
            arr_process.kill()
        else:
            subprocess.Popen(["docker", "container", "stop", container_name]).wait()
    else:
        print("Waiting for shutdown...")
        arr_process.wait()


def run(config):
    global arr_process
    if global_config.docker is None:
        print("Starting Arrnounced from source")
        arr_process = subprocess.Popen(
            [
                "coverage",
                "run",
                "-p",
                "--source",
                "../arrnounced/arrnounced",
                str(shutil.which("arrnounced")),
                "-v",
                "-c",
                "configs/" + config.config_file,
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
                current_directory
                + "/configs/"
                + config.config_file
                + ":/config/settings.toml",
                "-v",
                current_directory + "/trackers:/trackers",
                "-e",
                "TZ=" + timezone,
                "-e",
                "VERBOSE=Y",
                "weannounce/arrnounced:" + global_config.docker,
            ]
        )
