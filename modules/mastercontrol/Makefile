export USER_LIB_PATH=../libraries
#export AVRDUDE_ARD_BAUDRATE=14400
#export AVRDUDE_ARD_BAUDRATE=19200
#export AVRDUDE_ARD_BAUDRATE=9600
#export AVRDUDE_ARD_BAUDRATE=28800
#export AVRDUDE_ARD_BAUDRATE=38400
export AVRDUDE_ARD_BAUDRATE=57600
#export AVRDUDE_ARD_BAUDRATE=115200
#export AVRDUDE_ARD_PROGRAMMER=avrisp2
export ISP_PROG=avrisp2
export ISP_PORT = usb

all: mastercontrol.ino
	@$(MAKE) -f ../default_makefile all

%: force
	@$(MAKE) -f ../default_makefile $@

force: ;

.PHONY: panel

panel: panel_autogen.svg

panel_autogen.svg: create_panel.py
	python3 create_panel.py

