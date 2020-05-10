#!/bin/bash

if [ ! -f "../arrnounced/src/arrnounced.py" ]
then
  echo "Run script from test repo root"
  exit 1
fi

./run_tests.py $@
coverage combine
