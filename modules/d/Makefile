export USER_LIB_PATH=../libraries

export ISP_PROG=avrisp2
export ISP_PORT=usb

#include /usr/share/arduino/Arduino.mk

all: d_autogen.ino
	@$(MAKE) -f ../default_makefile all

%: force
	@$(MAKE) -f ../default_makefile $@

force: ;

.PHONY: panel manual


lookuptable_autogen.dat: config.py create_lookuptable.py
	python3 create_lookuptable.py

manual_tables_autogen.tex: config.py lookuptable_autogen.dat create_manual_table.py
	python3 create_manual_table.py

manual_description_autogen.tex: config.py create_manual_description.py
	python3 create_manual_description.py

d_autogen.ino: config.py lookuptable_autogen.dat create_cppfile.py d.ino.in
	python3 create_cppfile.py

panel: panel_autogen.svg


panel_autogen.svg: create_panel.py
	python3 create_panel.py

layout_autogen.tex: ../common/layout_generation/layout.py create_layout.py
	python3 create_layout.py

manual.pdf: manual.tex manual_description_autogen.tex manual_tables_autogen.tex layout_autogen.tex
	pdflatex manual.tex
	pdflatex manual.tex

manual: manual.pdf
