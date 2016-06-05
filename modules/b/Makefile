export USER_LIB_PATH=../libraries

#include /usr/share/arduino/Arduino.mk

all: autowires.cpp
	@$(MAKE) -f ../default_makefile all

%: force
	@$(MAKE) -f ../default_makefile $@

force: ;

autowires.cpp: autowires.cpp.in
	python3 create_wiring.py
