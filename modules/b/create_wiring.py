#!/usr/bin/python3
import sys
import random
import pygraphviz as pgv
import numpy as np

from common import *

sys.path.append("../../parts")
import top_plate
import laser_config

def get_output(input_values, outputs):
	return {output.label: output.get_value(input_values) for output in outputs}

def boolean_table(inputs, outputs):
	table = np.empty((2**len(inputs), len(inputs)+len(outputs),), dtype=np.bool)
	mesh = np.array(np.meshgrid(*[[False, True] for i in range(len(inputs))], indexing="ij"))
	mesh.shape = len(inputs), 2**len(inputs)
	mesh = mesh.T[:,::-1]

	for i in range(2**len(inputs)):
		table[i, :len(inputs)] = mesh[i]
		input_values = {input_names[-k-1]:table[i, k] for k in range(len(inputs))}
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

	tables = []
	output_integers = []

	for config_number, config in enumerate(configs):
		random.seed(config["random_seed"])

		g=pgv.AGraph(directed=True)

		num_gates = config["num_gates"]
		stretch_factor = config["stretch_factor"]

		inputs = []
		outputs = []

		for i in range(num_inputs):
			inputs.append(In(input_names[i]))

		for i in range(num_gates):
			gate_type = random.choice(config["gate_types"])
			gate = gate_type(*random.sample(Gate.all_gates[-int(num_inputs*stretch_factor):], 2))

		gates = Gate.all_gates[num_inputs:]

		for i in range(num_outputs):
			outputs.append(Out(output_names[i], gates[-(i+1)]))

		# prune graph
		continue_pruning = True
		while(continue_pruning):
			continue_pruning = False
			for gate in Gate.all_gates:
				gate.has_children = gate in outputs

			for gate in Gate.all_gates:
				for parent in gate.inputs:
					parent.has_children = True
			rest = [gate for gate in Gate.all_gates if gate.has_children]
			if len(rest) < len(Gate.all_gates):
				Gate.all_gates[:] = rest
				continue_pruning = True

		# generate graph output
		for gate in Gate.all_gates:
			gate.put_to_graph(g)

		g.layout(prog='dot')
		g.draw("wires_{}.pdf".format(config_number))

		# generate lookup table
		table = boolean_table(inputs, outputs)
		tables.append(table)
		output_table = table[:, len(inputs):]

		output_integers.append(np.sum(np.power(2, np.arange(num_outputs))[None, ::-1] * output_table, axis=1))

		for i in range(num_outputs):
			print("output {}: {} probability to be True".format(i, np.sum( output_table[:, i]) / (2**num_inputs) ))

		Gate.all_gates = []

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
		"// {}\n{{ ".format(configs[i]["title"])+np.array2string(oi, separator=", ")[1:-1]+"}" # remove [] on the outside
		for i, oi in enumerate(output_integers)])

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

	# generate panel svg
	with open("panel_autogen.svg", "w") as f:
		cut = laser_config.styles["cut"]
		engrave = laser_config.styles["engrave"]

		circle = """<circle style="{style}" cx="{}" cy="{}" r="{}"/>\n"""
		svg_start = """<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" width="{width}{units}" height="{height}{units}" viewBox="0 0 {width} {height}" id="{id}" version="1.1">\n""".format(
			width=top_plate.plate_width, height=top_plate.plate_width, id="panel", units="mm")
		svg_end = "</svg>\n"
		text = """<text x="{}" y="{}" font-family="monospace" text-anchor="middle" font-size="6" style="{style}">{}</text>\n"""

		names = input_names+output_names
		random.shuffle(names)

		f.write(svg_start)

		f.write(top_plate.make_top_plate("lt rt lb rb"))
		f.write(circle.format(top_plate.plate_width/2, -top_plate.hole_distance, laser_config.radius_led5, style=cut))

		num_cols = 4
		num_rows = 3

		h_padding = 15.0
		v_padding = 30.0

		text_offset = - 6.0

		h_distance = (100.0 - 2*h_padding)/(num_cols-1)
		v_distance = (100.0 - 2*v_padding)/(num_rows-1)

		for i, name in enumerate(names):
			x = i // num_rows * h_distance + h_padding
			y = i %  num_rows * v_distance + v_padding
			radius = laser_config.radius_led5 if name in input_names else laser_config.radius_switch

			f.write(circle.format(x, y, radius, style=cut))
			f.write(text.format(x, y+text_offset, name, style=engrave))

		x = (num_cols-1) * h_distance + h_padding
		y = (num_rows-1) * v_distance + v_padding

		f.write(circle.format(x, y, laser_config.radius_button_small, style=cut))
		f.write(text.format(x, y+text_offset, "RUN", style=engrave))



		f.write(svg_end)
	
	# generate manual figures
	with open("manual_figures_autogen.tex", "w") as f:
		invert_switches_table = ""
		for row in range(len(switch_inverts)//5):
			for col in range(5):
				i = col+row*5
				invert_switches_table += "xx{}x".format(switch_inverts[i])
				if col < 4:
					invert_switches_table += " &"
				else:
					invert_switches_table += " \\\\"

		f.write(r"""
		\begin{{table}}[b]
			\begin{{center}}
				\begin{{tabular}}{{ccccc}}
				{}
				\end{{tabular}}
			\end{{center}}
			\caption{{List of serial numbers with inverted switch directions (down=FALSE)}}
			\label{{tab:b_switch_inversion}}
		\end{{table}}
		""".format( invert_switches_table ))

		f.write(r"\newcommand{{\ledInversionNumbers}}{{{}}}".format(", ".join("xxxx"+l for l in led_inverts[:-1]) + " or xxxx" + led_inverts[-1]))

		for i, config in enumerate(configs):
			f.write(r"""
			\begin{{figure}}
				\begin{{center}}
				\includegraphics[scale=0.4]{{wires_{i}}}
				\caption{{Internal wiring for series {title}}}
				\end{{center}}
			\end{{figure}}""".format(i=i, title=config["title"]))

if __name__ == "__main__":
	main()

