#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

generateJob() {
  sed "s|.*ExecStart=.*|ExecStart=/bin/bash $DIR/install/autostart.sh $2|" "install/$1" > "install/${1}.temp"
  sudo mv "install/${1}.temp" "/etc/systemd/system/$1"
  sudo systemctl enable "${1/'.service'}"
}

#Function to install the systemd jobs
installJobs() {
  echo "Generating and installing systemd jobs:"
  generateJob "temp-report.service" "-t"
  generateJob "temp-listener.service" "-r"
  generateJob "temp-log.service" "-l"
  generateJob "temp-web.service" "-w"
  echo "Done"
}

installDeps() {
  sudo apt install htop libopenblas-dev libopenblas-base gcc g++ gfortran build-essential tk-dev libncurses5-dev libncursesw5-dev libreadline6-dev libdb5.3-dev libgdbm-dev libsqlite3-dev libssl-dev libbz2-dev libexpat1-dev liblzma-dev libffi-dev libatlas-base-dev -y
  sudo pip3 install -r requirements.txt
}

sudo apt-get install tmux -y

#Check for arguments
while [[ "$#" -gt 0 ]]; do case $1 in
  -h|--help) echo "Help:"; \
  echo "-h | --help        : Display this page and exit"; \
  echo "-d | --deps        : Install dependencies and exit"; \
  echo "-a | --autostart   : Generate and add systemd jobs"; \
  exit;;
  -d|--deps) echo "Installing dependencies:"; installDeps; exit;;
  -a|--autostart) echo "Generating and installing systemd jobs:"; installJobs; echo "Done generating and installing systemd jobs"; exit;;
  *) echo "Unknown parameter passed: $1"; exit 1;;
esac; shift; done

installDeps #Install build dependencies
installJobs #Generate and install systemd jobs

#Enable OneWire
if grep -Fxq "dtoverlay=w1-gpio" /boot/config.txt; then
    echo "OneWire is enabled"
else
    echo "OneWire is not enabled, enabling"
    sudo su root -c 'echo "dtoverlay=w1-gpio" >> /boot/config.txt'
    echo "OneWire is now enabled"
fi

#Generate config
python3 tempreport.py -c

#Add user credentials and tell them how to add addresses
echo "Use 'python3 tempreport.py -s' to set a sender email address"
echo "Use 'python3 tempreport.py -n' to set a sender name"
echo "Use 'python3 tempreport.py -p' to update the password for the sender address"
echo "Use 'python3 tempreport.py -a' to add or edit addresses on the mailing list"
echo "Add in the information and then reboot for the program to begin working"

echo "Installation complete"
