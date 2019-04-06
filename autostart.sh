#!/bin/bash
while [[ "$#" -gt 0 ]]; do case $1 in
  -t|--temp) echo "Starting temperature monitor:"; tmux new-session -d -s temp_report 'cd /home/pi/temp-report && /usr/bin/python3 /home/pi/temp-report/temp.py; exec bash -i';;
  -r|--reply) echo "Starting email listener and reply bot:"; tmux new-session -d -s temp_report 'cd /home/pi/temp-report && /usr/bin/python3 /home/pi/temp-report/listener.py; exec bash -i';;
  -l|--logger) echo "Starting logger:"; tmux new-session -d -s temp_report 'cd /home/pi/temp-report && /usr/bin/python3 /home/pi/temp-report/log.py; exec bash -i';;
  *) echo "Unknown parameter passed: $1"; exit 1;;
esac; shift; done
