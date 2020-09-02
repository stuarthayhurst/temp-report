#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

#Function to generate the systemd jobs
generatejobs() {
  echo "Generating systemd jobs:"
  sed "s|.*ExecStart=.*|ExecStart=/bin/bash $DIR/autostart.sh -t|" install/temp-report.service > install/temp-report-temp.service
  sed "s|.*ExecStart=.*|ExecStart=/bin/bash $DIR/autostart.sh -r|" install/temp-listener.service > install/temp-listener-temp.service
  sed "s|.*ExecStart=.*|ExecStart=/bin/bash $DIR/autostart.sh -l|" install/temp-log.service > install/temp-log-temp.service
  sed "s|.*ExecStart=.*|ExecStart=/bin/bash $DIR/autostart.sh -w|" install/temp-web.service > install/temp-web-temp.service
  echo "Done"
}

#Function to install the systemd jobs
installjobs() {
  echo "Installing systemd jobs:"
  sudo cp install/temp-report-temp.service /etc/systemd/system/temp-report.service
  sudo rm install/temp-report-temp.service
  sudo cp install/temp-listener-temp.service /etc/systemd/system/temp-listener.service
  sudo rm install/temp-listener-temp.service
  sudo cp install/temp-log-temp.service /etc/systemd/system/temp-log.service
  sudo rm install/temp-log-temp.service
  sudo cp install/temp-web-temp.service /etc/systemd/system/temp-web.service
  sudo rm install/temp-web-temp.service
  sudo systemctl enable temp-report
  sudo systemctl enable temp-listener
  sudo systemctl enable temp-log
  sudo systemctl enable temp-web
  echo "Done"
}

installdeps() {
  checktmux
  sudo apt update && sudo apt upgrade -y
  sudo apt install htop libopenblas-dev libopenblas-base gcc g++ gfortran build-essential tk-dev libncurses5-dev libncursesw5-dev libreadline6-dev libdb5.3-dev libgdbm-dev libsqlite3-dev libssl-dev libbz2-dev libexpat1-dev liblzma-dev libffi-dev -y
  sudo pip3 install --upgrade cython setuptools numpy w1thermsensor matplotlib flask gpiozero RPIO pigpio pytz tzlocal
}


sudo apt-get install tmux bc -y

#Check for arguments
while [[ "$#" -gt 0 ]]; do case $1 in
  -h|--help) echo "Help:"; \
  echo "-h | --help        : Display this page and exit"; \
  echo "-d | --deps        : Install dependencies and exit"; \
  echo "-a | --autostart    : Generate and add systemd jobs"; \
  exit;;
  -d|--deps) echo "Installing dependencies:"; installdeps; memcheck; installscipy; delmemcheck; exit;;
  -a|--autostart) echo "Generating and installing systemd jobs:"; generatejobs; installjobs; echo "Done generating and installing systemd jobs"; exit;;
  *) echo "Unknown parameter passed: $1"; exit 1;;
esac; shift; done

installdeps #Install build dependencies
generatejobs #Generate systemd jobs
installjobs #Install systemd jobs

#Enable OneWire
if grep -Fxq "dtoverlay=w1-gpio" /boot/config.txt
then
    echo "OneWire is enabled"
else
    echo "OneWire is not enabled, enabling"
    sudo su root -c 'echo "dtoverlay=w1-gpio" >> /boot/config.txt'
    echo "OneWire is now enabled"
fi

#Setup program files
python3 temp.py -cs

#Add user credentials and tell them how to add addresses
echo "Use 'python3 temp.py -s' to set a sender email address"
echo "Use 'python3 temp.py -n' to set a sender name"
echo "Use 'python3 temp.py -p' to update the password for the sender address"
echo "Use 'python3 temp.py -a' to add or edit addresses on the mailing list"
echo "Add in the information and then reboot for the program to begin working"


echo "Installation complete"
