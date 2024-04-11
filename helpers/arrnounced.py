from subprocess import Popen
import os
import shutil
import signal
import time
from helpers import config as global_config

container_name = "arrnounced_test"
current_directory = os.getcwd()
timezone = os.path.realpath("/etc/localtime")

arr_process = None


def stop(config):
    global arr_process
    print("Stopping Arrnounced")

    if global_config.docker is None:
        arr_process.send_signal(signal.SIGINT)
        arr_process.wait()
    else:
        Popen(["docker", "container", "stop", container_name]).wait()
        # Hopefully it stops in 3s
        time.sleep(3)


def run(config):
    global arr_process
    if global_config.docker is None:
        print("Starting Arrnounced from source")
        arr_process = Popen(
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
        arr_process = Popen(
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
