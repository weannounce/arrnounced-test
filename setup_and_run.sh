#!/bin/bash
RET=0

function get_logs()
{
  find_errors="warning|error|exception|backtrace|traceback|throw|task pending"
  cat data/*.log* | grep -iE "$find_errors" | ./filter_logs.py
}

RUNS=1

while getopts ":n:" o; do
    case "${o}" in
        n)
            RUNS=${OPTARG}
            ;;
        *)
            echo "Unknown flag"
            exit 1
            ;;
    esac
done
shift $((OPTIND-1))

if ! [[ $VIRTUAL_ENV =~ arrnounced-test ]]
then
  echo "Must run in poetry virtual env (poetry run ./setup_and_run.sh)"
  exit 1
fi

run_tests()
{
  echo "Removing old log files"
  rm -vrf data/*.log*

  #py-spy record --idle -o profile.svg -- ./run_tests.py "$@" || RET=1
  ./run_tests.py "$@" || return 1
  coverage combine
  coverage html

  error_logs="$(get_logs)"
  if [ -n "$error_logs" ]
  then
    echo ""
    echo "Found error logs:"
    echo "$error_logs"
    return 1
  fi
}

start_date=$(date)

for i in $(seq "$RUNS")
do
  echo "Run number $i in progress"
  run_tests "$@" || { RET=1; break; }
done

echo "Start $start_date"
echo "End $(date)"
echo "Exiting on run number $i"

exit "$RET"
