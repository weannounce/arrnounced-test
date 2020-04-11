#!/bin/bash

if [ ! -f "../arrnounced/src/arrnounced.py" ]
then
  echo "Run script from test repo root"
  exit 1
fi

../arrnounced/src/arrnounced.py -v -c test_settings.cfg -d data -t trackers &
trap 'kill %1' EXIT

echo "Waiting for Arrnounced to finish start up..."
sleep 15

./run_tests.py

#jobs
#kill %1
