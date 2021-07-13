# temp-report
  - A project to report the temperature of an area to a mailing list when it falls out of a threshold, from a Raspberry Pi
  - Handles logging, graphing, mailing a list, replying to requests for data and displaying a webpage
  - I'm mostly done with this project, future updates will usually be bug fixes
  - Basically, the project is archived

## Dependencies:
  - All required and recommended packages are automatically installed when running the installer, except `scipy`, which needs to be installed manually
  - ### Python / Pip
    - Python 3.6+
    - cython
    - flask
    - matplotlib
    - numpy
    - pillow
    - scipy
    - setuptools
    - w1thermsensor

  - ### Source / Package Manager
    - build-essential
    - gcc && g++
    - gfortran
    - libopenblas-dev && libopenblas-base && libatlas-base-dev
    - tmux

## Installation:
  - Make sure the wiring for the sensor is complete (Diagram can be found at the end)
  - `git clone https://github.com/stuarthayhurst/temp-report.git`
  - Install `scipy`, `python` (3.6+) and `pip3`
  - Install other dependencies listed in the previous section
  - Enable OneWire: `echo "dtoverlay=w1-gpio" | sudo tee -a /boot/config.txt > /dev/null`
  - Generate the configs: `python3 tempreport.py -c`
  - Run `python3 tempreport.py --help`, and set a sender email address, name and password
  - Run `python3 tempreport.py -a` to setup a mailing list
  - Change config values to your liking, in `data/config.py`

## Commands and help:
  - Use `python3 tempreport.py -h` to view help
  - Use `tmux att -t temp_report` to view the program
  - Use `tmux att -t temp_listener` to view the email reply bot
  - Use `tmux att -t temp_log` to view the automatic temperature log
  - Use `tmux att -t temp_web` to view the web frontend log
  - Run `./install/setup.sh` to allow the program to start on boot
  - After an update, add any missing config values from `data/config-template.py` to `data/config.py`
  - **A Pi 3 or better is strongly recommended**
  - See wiki for more information

## Wiring diagram:
![alt text](https://farm5.staticflickr.com/4215/35139160190_cea3435a09_b_d.jpg)
  - Diagram credit: [Les Pounder](https://bigl.es/author/les/ "Les Pounder")

## License:
  - GNU GENERAL PUBLIC LICENSE (v3)
