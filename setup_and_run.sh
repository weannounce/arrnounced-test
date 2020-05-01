#!/bin/bash

readonly container_name="arrnounced_test"
readonly current_directory="$(readlink -f .)"
readonly timezone="$(readlink -f /etc/localtime | sed -r 's#.*/(.*/.*)#\1#')"

if [ ! -f "../arrnounced/src/arrnounced.py" ]
then
  echo "Run script from test repo root"
  exit 1
fi

while getopts "d:" opt; do
  case ${opt} in
    d )
      readonly docker_version="$OPTARG"
      ;;
    * )
      exit 1
      ;;
  esac
done
shift $((OPTIND -1))

if [ -n "$docker_version" ]
then
  echo "Starting docker..."
  docker run --name "$container_name" \
             --rm \
             --net=host \
             --user $(id -u) \
             -d \
             -v "$current_directory/data:/config" \
             -v "$current_directory/trackers:/trackers" \
             -e TZ="$timezone" \
             -e VERBOSE=Y \
             "weannounce/arrnounced:$docker_version"
  trap "docker stop $container_name"  EXIT
else
  echo "Running from source..."
  coverage run --source ../arrnounced/src ../arrnounced/src/arrnounced.py -v -c data/settings.cfg -d data -t trackers &
  trap 'curl -s http://localhost:3467/shutdown' EXIT
fi

./run_tests.py
