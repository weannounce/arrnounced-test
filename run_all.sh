#!/bin/bash

set -eo pipefail

failed()
{
  echo "failed with Python version $(poetry run python --version)" >&2
  exit 1
}

poetry env use 3.7
poetry run ./setup_and_run.sh || failed
poetry env use 3.8
poetry run ./setup_and_run.sh || failed
poetry env use 3.9
poetry run ./setup_and_run.sh || failed
