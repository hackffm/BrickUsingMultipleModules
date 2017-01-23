export USER_LIB_PATH=../libraries

export ISP_PROG=avrisp2
export ISP_PORT=usb


#include /usr/share/arduino/Arduino.mk

all: wires_autogen.cpp
	@$(MAKE) -f ../default_makefile all

%: force
	@$(MAKE) -f ../default_makefile $@

force: ;

.PHONY: panel manual

panel: panel_autogen.svg

manual: manual_en.pdf manual_de.pdf manual_chde.pdf

manual_%.pdf: manual_figures manual_figures_autogen.tex manual.tex layout_autogen.tex
	pdflatex -jobname manual_$* "\input{../common/$*.tex}\input{manual.tex}"
	pdflatex -jobname manual_$* "\input{../common/$*.tex}\input{manual.tex}"

wires_autogen.cpp: autowires.cpp.in lookuptable_autogen.npy
	python3 create_lookupcode.py

cheatsheet_autogen.html: lookuptable_autogen.npy
	python3 create_cheatsheet.py

manual_figures_autogen.tex: common.py create_figurelist.py logic_examples
	python3 create_figurelist.py

logic_examples: create_logic_examples.py
	python3 create_logic_examples.py

manual_figures: gates_autogen.dat
	python3 create_figures.py

gates_autogen.dat: common.py
	python3 create_gatelist.py

wires_autogen.cpp: autowires.cpp.in lookuptable_autogen.npy
	python3 create_lookupcode.py

lookuptable_autogen.npy: gates_autogen.dat
	python3 create_lookuptable.py

panel_autogen.svg: common.py ../../parts/laser_config.py ../../parts/top_plate.py
	python3 create_panel.py

layout_autogen.tex: ../common/layout_generation/layout.py create_layout.py common.py
	python3 create_layout.py
