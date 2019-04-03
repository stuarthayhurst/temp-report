# temp-report
A small project to report the temperature of a room to anyone on the mailing list when it reaches a certain temperature with an integrated csv editor and handle email replies

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

- Make sure to install as `pi` in `/home/pi`

- `git clone https://github.com/Dragon8oy/temp-report.git`
- `./install.sh`

 - See wiki for manual installation

## Commands and notes:

- Add `@reboot tmux new-session -d -s temp_report 'cd /path/to/install && /path/to/python/install /path/to/install/temp.py; exec bash -i'` to `crontab -e` to have the program start on boot
- Add `@reboot tmux new-session -d -s temp_listener 'cd /path/to/install && /path/to/python/install /path/to/install/listener.py; exec bash -i'` to `crontab -e` to have the email reply bot start on boot
- Use `tmux att -t temp_report` to view the program
- After an update, run `python3.6 temp.py -cs` to update the config with any new lines
- Use `python3.6 temp.py -h` to view help
- Make sure OneWire is enabled
- See wiki for more information

## Wiring diagram:

![alt text](https://farm5.staticflickr.com/4215/35139160190_cea3435a09_b_d.jpg)
- Diagram credit: [Les Pounder](https://bigl.es/author/les/ "Les Pounder")
