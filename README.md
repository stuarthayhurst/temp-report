# temp-report
A small project to create a system that can handle the output from a Pi temperature logger.
The system maintains a mail-list and will respond to mail requests. Reports include temperature charts and are generated when the temperature moves outside of a defined range or an email is received requesting a report.

Temp-report Version: 1.1.0
Temp-web Version: 0.8.0

## Dependencies:
All required and recommended packages are automatically installed when running the installer

- ### Python / Pip
  * Python 3.6+
  * flask
  * w1thermsensor
  * matplotlib
  * scipy
  * numpy
  * cython
  * setuptools

- ### Source / Package Manager
  * Tmux
  * libopenblas-dev && libopenblas-base
  * gcc && g++
  * build-essential && gfortran
-   #### Recommended:
    * Htop


## Installation:

- Make sure the wiring for the sensor is complete first
- `git clone https://github.com/Dragon8oy/temp-report.git`
- `./install.sh`

 - See wiki for manual installation

## Commands and notes:

- Use `python3 temp.py -h` to view help
- Use `tmux att -t temp_report` to view the program
- Use `tmux att -t temp_listener` to view the email reply bot
- Use `tmux att -t temp_log` to view the automatic temperature log
- Run `./install.sh -s` to allow the program to start on boot
- After an update, run `python3 temp.py -cs` to update the config with any new lines
- You can use `./import.sh -h` to import and export csv files
- See wiki for more information

## Wiring diagram:

![alt text](https://farm5.staticflickr.com/4215/35139160190_cea3435a09_b_d.jpg)
- Diagram credit: [Les Pounder](https://bigl.es/author/les/ "Les Pounder")
