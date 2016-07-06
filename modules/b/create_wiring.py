#!/usr/bin/python3
import sys
import random
import pickle
import numpy as np

from common import *

def get_output(input_values, outputs):
	return {output.label: output.get_value(input_values) for output in outputs}

def boolean_table(num_inputs, outputs):
	table = np.empty((2**num_inputs, num_inputs+len(outputs),), dtype=np.bool)
	mesh = np.array(np.meshgrid(*[[False, True] for i in range(num_inputs)], indexing="ij"))
	mesh.shape = num_inputs, 2**num_inputs
	mesh = mesh.T[:,::-1]

	for i in range(2**num_inputs):
		table[i, :num_inputs] = mesh[i]
		input_values = {input_names[-k-1]:table[i, k] for k in range(num_inputs)}
		for j, o in enumerate(outputs):
			table[i, -j-1] = o.get_value(input_values)
	return table

template_pininput = """
	if(digitalRead(PIN_{name}) == HIGH)
		input_value |= (1<<{bit});
"""

def main():
	num_inputs = len(input_names)
	num_outputs = len(output_names)
	tables = np.empty((len(configs), 2**num_inputs, num_inputs+num_outputs,), dtype=np.bool)

	with open(GATE_FILE, "rb") as f:
		gates_per_config = pickle.load(f)
	for config_number, config in enumerate(configs):
		gates = gates_per_config[config_number]
		outputs = gates[-len(output_names):]

		# generate lookup table
		table = boolean_table(len(input_names), outputs)
		tables[config_number,] = table

		for i in range(num_outputs):
			print("output {}: {} probability to be True".format(i, np.sum( table[:, num_inputs+i]) / (2**num_inputs) ))
	
	np.save(TABLE_FILE, tables)

def main2():
	num_inputs = len(input_names)
	num_outputs = len(output_names)
	tables = np.load(TABLE_FILE)
	# generate cheatsheet
	with open("cheatsheet_autogen.html","w") as f:
		f.write("""<html>\n<head><title>Module: Gates - Cheatsheet</title></head>\n<body>\n""")
		for i, table in enumerate(tables):
			f.write("""<div style="position:absolute;width:{}%;left:{}%;">\n""".format(100//len(tables), 100//len(tables)*i))
			f.write("<p>{}</p>\n".format(configs[i]["title"]))
			f.write("""<table cellborder="1">\n<thead><tr>""")
			for i in input_names:
				f.write("<td>{}</td>".format(i))
			for o in reversed(output_names):
				f.write("<td>{}</td>".format(o))
			f.write("</tr></thead>\n")
			for row in table:
				f.write("<tr>")
				for col in row:
					f.write("<td>{}</td>".format("X" if col else "O"))
				f.write("</tr>\n")
			f.write("</table>\n")
			f.write("</div>\n")
		f.write("</body></html>\n")

	# generate cpp file
	pininput = "\n".join([template_pininput.format(name=name, bit=i) for i, name in enumerate(output_names)])
	pininput += "\n\tif(invert_switches(serial_number))\n\t\tinput_value ^= {};\n".format(2**num_outputs-1)

	lookuptable = ",\n".join([
		"// {}\n{{ ".format(configs[i]["title"])+np.array2string(np.sum(np.power(2, np.arange(num_outputs))[None, ::-1] * table[:, num_inputs:], axis=1), separator=", ")[1:-1]+"}" # remove [] on the outside
		for i in range(len(configs))])

	setup  = "\n".join(["""\tpinMode(PIN_{name}, OUTPUT);""".format(name=name) for name in input_names])
	setup += "\n\n"
	setup += "\n".join(["""\tpinMode(PIN_{name}, INPUT_PULLUP);""".format(name=name) for name in output_names])

	setdisplay = "\tif(invert_leds(serial_number))\n\t\trandom_value ^= 0xFF;\n\n"
	setdisplay += "\n".join(["""\tdigitalWrite(PIN_{name}, random_value & (1<<{bit}) ? HIGH : LOW);""".format(name=name, bit=i) for i, name in enumerate(input_names)])

	invert_leds_string = "\n".join(("""\tif(serial_number[4]=='{}') return 1;""".format(l) for l in led_inverts))

	invert_switches_string = "\n".join(("""\tif( (serial_number[2]=='{}') && (serial_number[3]=='{}') ) return 1;""".format(s[0], s[1]) for s in switch_inverts))

	random_value_bitmask = 2**num_inputs-1

	with open("autowires.cpp.in", "r") as f:
		template = f.read()

	with open("wires_autogen.cpp","w") as f:
		f.write("// This file has been generated automatically! Do not modify!\n")
		f.write(template.format(
			lookuptable=lookuptable,
			pininput=pininput,
			setup=setup,
			setdisplay=setdisplay,
			invert_switches = invert_switches_string,
			invert_leds = invert_leds_string,
			random_value_bitmask = random_value_bitmask,
			num_tables=len(tables),
			num_combinations=len(tables[0])))

if __name__ == "__main__":
	main()
	main2()
