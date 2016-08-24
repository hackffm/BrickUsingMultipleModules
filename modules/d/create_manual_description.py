#!/usr/bin/python3
import config

with open("manual_description_autogen.tex", "w") as f:
	for command, mode in config.button_modes.items():
		f.write(r"{} & {} \\".format(command, mode["description"])+"\n")
