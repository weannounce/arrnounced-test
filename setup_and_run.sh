#!/bin/bash

allowed_errors=(
"WARNING:ANNOUNCEMENT +- Could not build var 'torrentName', missing variable 'if_setregex1'"
"WARNING:ANNOUNCEMENT +- Could not build var 'torrentUrl', missing variable 'extractone1'"
"WARNING:ANNOUNCEMENT +- Could not build var 'torrentUrl', missing variable 'setregex2'"
"WARNING:ANNOUNCEMENT +- Extract: Variable 'extract1' did not match regex '.tags: ....'"
"WARNING:ANNOUNCEMENT +- Extract: Variable 'extract2' did not match regex '.....;....'"
"WARNING:ANNOUNCEMENT +- ExtractOne: No matching regex found"
"WARNING:ANNOUNCEMENT +- ExtractTags: Could not extract tags, variable 'varreplace1' not found"
"WARNING:ANNOUNCEMENT +- HTTP header .e.g. cookie. in tracker configuration not supported. This might cause problems downloading the torrent file."
"WARNING:ANNOUNCEMENT +- If: Could not check condition, variable 'setregex1' not found"
"WARNING:ANNOUNCEMENT +- Missing torrent URL"
"WARNING:ANNOUNCEMENT +- Missing torrent name"
"WARNING:ANNOUNCEMENT +- SetRegex: Could not set variable, 'extract4' not found"
"WARNING:ANNOUNCEMENT +- SetRegex: Could not set variable, 'extractone1' not found"
"WARNING:ANNOUNCEMENT +- VarReplace: Could not replace, variable 'extract5' not found"
"WARNING:ANNOUNCE_PARSER +- Single: No match found for 'this is a name  -  cow. ¤..- #angry#  -  pasta and sauce'"
"WARNING:TRACKER_CONF +- single: Tracker seems to require cookies to download torrent file. Sonarr.Radarr.Lidarr API does not support cookies"
"WARNING:WEB-UI *- Could not find the requested backend 'nonexistent'"
"WARNING:IRC:.+ - Unknown command: "
)

function get_logs()
{
  logs="$(cat data/*.log* | grep -iE "warning|error|exception|backtrace|throw")"
  for l in "${allowed_errors[@]}";
  do
    logs="$(echo "$logs" | sed -re "/$l/d")"
  done
  echo "$logs"
}

if [ ! -f "../arrnounced/src/arrnounced.py" ]
then
  echo "Run script from test repo root"
  exit 1
fi

echo "Removing old log files"
rm -vrf data/*.log*

./run_tests.py "$@"
coverage combine
coverage html

error_logs="$(get_logs)"
if [ -n "$error_logs" ]
then
  echo ""
  echo "Found error logs:"
  echo "$error_logs"
fi
