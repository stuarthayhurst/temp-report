# temp-report
A small project to report the temperature of a room to anyone on the mailing list when it reaches a certain temperature with an integrated csv editor

## Dependencies:

- ### Python / Pip
  * Python 3.6+
  * w1thermsensor
  * matplotlib

- ### Source / Package Manager
  * Tmux

## Installation:

- `git clone https://github.com/Dragon8oy/temp-report.git`
- `sudo pip3.6 install w1thermsensor matplotlib`
- `sudo apt install tmux`

## Commands and notes:

- Add `@reboot tmux new-session -d -s temp_report 'python3.6 /path/to/install/temp.py; exec bash -i'` to `crontab -e` to have the program start on boot
- Use `tmux att -t temp_report` to view the program
- Use `python3.6 temp.py -h` to view help
- Make sure OneWire is enabled

## Wiring diagram:

![alt text](https://farm5.staticflickr.com/4215/35139160190_cea3435a09_b_d.jpg)
- Credit: [Les Pounder](https://bigl.es/author/les/ "Les Pounder")
