# BrickUsingMultipleModules

More info about gameplay and pictures on https://hackerspace-ffm.de/wiki/index.php?title=BrickUsingMultipleModules

## Build dependencies
Use `git clone --recursive` to get the Adafruit libraries necessary for some modules.
### Modules
* make
* pdflatex
* arduino-mk
* python3
* PyGraphViz (Gates module)

### Gamemaster
* python2
* pygame

### GUI
* python3
* tkinter for python3

## Build commands
### Program an arduino
`make upload` in module folder

### Manual
`make manual` in module folder or `make manual_en.pdf` if you want to skip the german manuals.

### Frontpanel
`make panel` in module folder

## Gamemaster
`./gamemaster.py --help` in `master/gamemaster` to get info about command line usage.

## GUI
`./master_gui.py HOSTNAME` in `master/gui` to connect to gamemaster running on `HOSTNAME`.
