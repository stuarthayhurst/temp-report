#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

#Function to make swap space
addswap() {
  sudo /bin/dd if=/dev/zero of=/var/swap.temp bs=1M count=1024
  sudo /sbin/mkswap /var/swap.temp
  sudo chmod 600 /var/swap.temp
  sudo /sbin/swapon /var/swap.temp
}

#Function to remove swap space
delswap() {
  sudo swapoff /var/swap.temp
  sudo rm /var/swap.temp
}

#Function to generate the systemd jobs
generatejobs() {
    echo "Generating systemd jobs:"
    sed "s|ExecStart=|ExecStart=/bin/bash $DIR/autostart.sh -t|" install/temp-report.service > temp.txt && mv temp.txt install/temp-report.service
    sed "s|ExecStart=|ExecStart=/bin/bash $DIR/autostart.sh -r|" install/temp-listener.service > temp.txt && mv temp.txt install/temp-listener.service
    sed "s|ExecStart=|ExecStart=/bin/bash $DIR/autostart.sh -l|" install/temp-log.service > temp.txt && mv temp.txt install/temp-log.service
    echo "Done"
}

#Function to install the systemd jobs
installjobs() {
  echo "Installing systemd jobs:"
  sudo cp install/temp-* /etc/systemd/system/
  sudo systemctl start temp-report
  sudo systemctl start temp-listener
  sudo systemctl start temp-log

  sudo systemctl enable temp-report
  sudo systemctl enable temp-listener
  sudo systemctl enable temp-log
    echo "Done"
}

installpython() {
  git clone -b 3.7 https://github.com/python/cpython.git
  cd cpython
  ./configure
  make -j4
  make -j4 test
  sudo make install
  cd ../ && rm -rf cpython/
}

sudo apt-get install tmux git -y

#Get latest version
PULL=`git pull`
echo $PULL
if echo $PULL |grep 'install.sh'; then
    echo "Installer script was updated, restarting"
    /bin/bash $DIR/install.sh
    exit
else
    echo "No updates found for the installer, continuing"
fi

while [[ "$#" -gt 0 ]]; do case $1 in
  -s|--start-up) echo "Generating and installing systemd jobs:"; generatejobs; installjobs; echo "Done generating and installing systemd jobs";;
  *) echo "Unknown parameter passed: $1"; exit 1;;
esac; shift; done

if ! { [ "$TERM" = "screen" ] && [ -n "$TMUX" ]; } then
  tmux new-session -d -s temp_installer '/bin/bash '$DIR'/install.sh; exec bash -i'
  tmux att -t temp_installer
  exit
fi

PYVER=$(python3 -V 2>&1 | grep -Po '(?<=Python )(.+)')
shopt -s extglob
read -r Z _ <<< "${PYVER//[^[:digit:] ]/}"
PYNUMS=${Z##+(0)}
SHORT="${PYNUMS:0:2}" ; echo "${SHORT}"

if [ "$SHORT" -gt "35" ]
then
  echo "Sufficient Python version found"
else
  echo "Insufficient Python version found" && echo "Press enter to install Python 3.7" && echo "Press CTRL+C to quit"
  read CONTINUE
  installpython
  exit
fi

#Scipy
MEM=$(grep MemTotal /proc/meminfo | awk '{print $2}' | xargs -I {} echo "scale=4; {}/1024^2" | bc)

if [[ "$MEM" > "1.5" ]]
then
  echo "Enough RAM detected, not generating a new swapfile"
else
  echo "Not enough RAM detected, generating a new swapfile"
  addswap
fi

sudo apt-get install libopenblas-dev libopenblas-base gcc gfortran -y
sudo pip3 install cython setuptools numpy
git clone https://github.com/scipy/scipy.git
cd scipy && python3 setup.py build && sudo python3 setup.py install && cd ../ && rm -rf scipy

#Install temp-report
sudo apt-get install htop -y
sudo pip3 install w1thermsensor matplotlib pillow

generatejobs
installjobs

#Enable OneWire
if grep -Fxq "dtoverlay=w1-gpio" /boot/config.txt
then
    echo "OneWire is enabled"
else
    echo "OneWire is not enabled, enabling"
    sudo echo "dtoverlay=w1-gpio" >> /boot/config.txt
    echo "OneWire is now enabled"
fi

#Setup program files
python3 temp.py -cs

#Add user credentials and tell them how to add addresses
echo "Use 'python3 temp.py -s' to set a sender email address"
echo "Use 'python3 temp.py -n' to set a sender name"
echo "Use 'python3 temp.py -p' to update the password for the sender address"
echo "Use 'python3 temp.py -a' to add or edit addresses on the mailing list"

#Cleanup
MEM=$(grep MemTotal /proc/meminfo | awk '{print $2}' | xargs -I {} echo "scale=4; {}/1024^2" | bc)

if [[ "$MEM" > "1.5" ]]
then
  echo "No temporary swapfile to remove"
else
  echo "Removing temporary swapfile"
  delswap
fi

rm -rf install/
echo "Installation complete"
