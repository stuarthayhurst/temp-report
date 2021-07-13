#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

generateJob() {
  sed "s|.*ExecStart=.*|ExecStart=/bin/bash $DIR/autostart.sh $2|" "$1" > "${1}.temp"
  sudo mv "${1}.temp" "/etc/systemd/system/$1"
  sudo systemctl enable "${1/'.service'}"
}

installJobs() {
  echo "Generating and installing systemd jobs:"
  generateJob "temp-report.service" "-t"
  generateJob "temp-listener.service" "-r"
  generateJob "temp-log.service" "-l"
  generateJob "temp-web.service" "-w"
  echo "Done"
}

installJobs #Generate and install systemd jobs
