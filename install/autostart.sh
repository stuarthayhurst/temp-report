#!/bin/bash
workDir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "${workDir}/../" || exit 1
workDir="$(pwd)"

while [[ "$#" -gt 0 ]]; do case $1 in
  -t|--temp) echo "Starting temperature monitor:"; tmux new-session -d -s temp_report "cd $workDir && /usr/bin/python3 $workDir/tempreport.py; exec bash -i";;
  -r|--reply) echo "Starting email listener and reply bot:"; tmux new-session -d -s temp_listener "cd $workDir && /usr/bin/python3 $workDir/listener.py; exec bash -i";;
  -l|--logger) echo "Starting logger:"; tmux new-session -d -s temp_log "cd $workDir && /usr/bin/python3 $workDir/log.py; exec bash -i";;
  -w|--web) echo "Starting webpage:"; tmux new-session -d -s temp_web "cd $workDir/web && sudo /usr/bin/python3 $workDir/web/tempweb.py; exec bash -i";;
  *) echo "Unknown parameter passed: $1"; exit 1;;
esac; shift; done
