#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

#Function to make swap space
addswap() {
  sudo /bin/dd if=/dev/zero of=/var/swap.temp bs=1M count=2048
  sudo /sbin/mkswap /var/swap.temp
  sudo chmod 600 /var/swap.temp
  sudo /sbin/swapon /var/swap.temp
}

#Function to remove swap space
delswap() {
  sudo swapoff /var/swap.temp
  sudo rm /var/swap.temp
}

#Checks for enough memory
memcheck() {
  MEM=$(grep MemTotal /proc/meminfo | awk '{print $2}' | bc)
  if [[ "$MEM" -gt "2097152" ]]
  then
    echo "Enough RAM detected, not generating a new swapfile"
  else
    echo "Not enough RAM detected, generating a new swapfile"
    addswap
  fi
}

#Works out whether or not a new swapfile was created
delmemcheck() {
  MEM=$(grep MemTotal /proc/meminfo | awk '{print $2}' | bc)
  if [[ "$MEM" -gt "2097152" ]]
  then
    echo "No temporary swapfile to remove"
  else
    echo "Removing temporary swapfile"
    delswap
  fi
}

#Function to generate the systemd jobs
generatejobs() {
  echo "Generating systemd jobs:"
  sed -i 's|.*ExecStart=.*|ExecStart=/bin/bash $DIR/autostart.sh -t|' install/temp-report.service
  sed -i 's|.*ExecStart=.*|ExecStart=/bin/bash $DIR/autostart.sh -r|' install/temp-listener.service
  sed -i 's|.*ExecStart=.*|ExecStart=/bin/bash $DIR/autostart.sh -l|' install/temp-log.service
  echo "Done"
}

#Function to install the systemd jobs
installjobs() {
  echo "Installing systemd jobs:"
  sudo cp install/temp-* /etc/systemd/system/
  sudo systemctl enable temp-report
  sudo systemctl enable temp-listener
  sudo systemctl enable temp-log
  echo "Done"
}

#Function to build and install python
installpython() {
  git clone -b 3.7 https://github.com/python/cpython.git
  cd cpython
  ./configure
  make -j 4
  sudo make -j 4 altinstall
  sudo update-alternatives --install /usr/bin/pip3 pip3 /usr/local/bin/pip3.7 1
  sudo update-alternatives --set pip3 /usr/local/bin/pip3.7
  sudo update-alternatives --install /usr/bin/python3 python3 /usr/local/bin/python3.7 1
  sudo update-alternatives --set python3 /usr/local/bin/python3.7
  sudo pip3 install --upgrade pip
  cd ../ && sudo rm -rf cpython/
}

#Installs scipy
installscipy() {
  git clone https://github.com/scipy/scipy.git
  cd scipy && python3 setup.py build && sudo python3 setup.py install && cd ../ && sudo rm -rf scipy
}

#Installs dependencies
installdeps() {
  checktmux
  sudo apt update && sudo apt upgrade -y
  sudo apt install htop libopenblas-dev libopenblas-base gcc g++ gfortran build-essential tk-dev libncurses5-dev libncursesw5-dev libreadline6-dev libdb5.3-dev libgdbm-dev libsqlite3-dev libssl-dev libbz2-dev libexpat1-dev liblzma-dev libffi-dev zlib1g-dev libffi-dev libjpeg9 libjpeg9-dev -y
}

#Checks for tmux
checktmux() {
  if ! { [ "$TERM" = "screen" ] && [ -n "$TMUX" ]; } then
    echo "Moving installer to a tmux session:"
    tmux new-session -d -s temp_installer 'echo "Installer moved to a tmux session, restarting"; /bin/bash '$DIR'/install.sh '$1'; exec bash -i'
    tmux att -t temp_installer
    exit
  fi
}

sudo apt-get install tmux bc -y

#Get latest version
PULL=`git pull`
echo $PULL
if echo $PULL |grep 'install.sh'; then
    echo "Installer script was updated, restarting"
    /bin/bash $DIR/install.sh $1
    exit
else
    echo "No updates found for the installer, continuing"
fi

#Check for arguments
while [[ "$#" -gt 0 ]]; do case $1 in
  -h|--help) echo "Help:"; echo "-h | --help        : Display this page and exit"; echo "-d | --deps        : Install dependencies and exit"; echo "-p | --python      : Install Python and exit"; echo "-s | --start-up    : Generate and add systemd jobs"; echo "-r | --remove-swap : Remove the swapfile the program creates if it crashed before cleanup"; exit;;

  -d|--deps) echo "Installing dependencies:"; installdeps; memcheck; installscipy; delmemcheck; exit;;

  -p|--python) echo "Installing Python and dependencies:"; installdeps; memcheck; installpython; delmemcheck; exit;;

  -s|--start-up) echo "Generating and installing systemd jobs:"; generatejobs; installjobs; echo "Done generating and installing systemd jobs"; exit;;

  -r|--remove-swap) echo "Removing swapfile:"; delswap; echo "Done"; exit;;

  *) echo "Unknown parameter passed: $1"; exit 1;;
esac; shift; done

#Check for tmux
checktmux

#Check RAM size before compiling anything
memcheck

#Install build dependencies
installdeps

#Check Python version and build Python 3.7
PYVER=$(python3 -V 2>&1 | grep -Po '(?<=Python )(.+)')
shopt -s extglob
read -r Z _ <<< "${PYVER//[^[:digit:] ]/}"
PYNUMS=${Z##+(0)}
SHORT="${PYNUMS:0:2}" ; echo "${SHORT}"

if [ "$SHORT" -gt "35" ]
then
  echo "Sufficient Python version found"
else
  echo "Insufficient Python version found" && echo "Python 3.7 will now be installed, Press CTRL+C quickly to quit"
  installpython
fi

#Install build and program dependencies
sudo pip3 install --upgrade cython setuptools numpy w1thermsensor matplotlib pillow

#Build and install Scipy
installscipy

#Install temp-report systemd jobs

generatejobs
installjobs

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

#Cleanup
delmemcheck

echo "Installation complete"
