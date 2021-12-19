#!/bin/bash
RET=0

function get_logs()
{
  find_errors="warning|error|exception|backtrace|traceback|throw|task pending"
  cat data/*.log* | grep -iE "$find_errors" | ./filter_logs.py
}

if ! [[ $VIRTUAL_ENV =~ arrnounced-test ]]
then
  echo "Must run in poetry virtual env (poetry run ./setup_and_run.sh)"
  exit 1
fi

echo "Removing old log files"
rm -vrf data/*.log*

#py-spy record --idle -o profile.svg -- ./run_tests.py "$@" || RET=1
./run_tests.py "$@" || RET=1
coverage combine
coverage html

error_logs="$(get_logs)"
if [ -n "$error_logs" ]
then
  echo ""
  echo "Found error logs:"
  echo "$error_logs"
  RET=1
fi

exit "$RET"
