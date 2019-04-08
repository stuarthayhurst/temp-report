# temp-report
A small project to create a system that can handle the output from a Pi temperature logger.
The system maintains a mail-list and will respond to mail requests. Reports include temperature charts and are generated when the temperature moves outside of a defined range or an email is received requesting a report. 

## Dependencies:

- ### Python / Pip
  * Python 3.6+
  * w1thermsensor
  * matplotlib
  * pillow
  * scipy

- ### Source / Package Manager
  * Tmux
-   #### Recommended:
    * Htop

- ### Build:
-   #### Python / Pip:
    * numpy - required for scipy after build
    * cython
    * setuptools

-   #### Source / Package Manager:
    * libopenblas-base, libopenblas-dev
    * gcc
    * gfortran

## Installation:

- `git clone https://github.com/Dragon8oy/temp-report.git`
- `./install.sh`

 - See wiki for manual installation

## Commands and notes:

- Run `./install.sh -s` to allow the program to start on boot
- Use `tmux att -t temp_report` to view the program
- After an update, run `python3 temp.py -cs` to update the config with any new lines
- Use `python3 temp.py -h` to view help
- Make sure OneWire is enabled
- See wiki for more information

## Wiring diagram:

![alt text](https://farm5.staticflickr.com/4215/35139160190_cea3435a09_b_d.jpg)
- Diagram credit: [Les Pounder](https://bigl.es/author/les/ "Les Pounder")
