#!/usr/bin/python3
import sys
import random
import pygraphviz as pgv
import numpy as np

functions = {
	"&": lambda a, b: a and b,
	"|": lambda a, b: a or b,
	"=1": lambda a, b: a ^ b,
	"nor": lambda a, b: not (a or b),
	"nand": lambda a, b: not (a and b),
	"out": lambda a, b: False
}

class Gate(object):
	running_number = 0
	all_gates = []
	def __init__(self):
		self.number = Gate.running_number
		Gate.running_number += 1
		Gate.all_gates.append(self)
		self.label = None

		self.children = False

		self.node_kwargs = {}

	def __str__(self):
		return str(self.number)

	def put_to_graph(self, graph):
		graph.add_node(self, label=self.fname if self.label is None else self.label, **self.node_kwargs)
		for inp in self.inputs:
			graph.add_edge(inp, self)

	def get_value(self, inputs):
		return self.func(*(parent.get_value(inputs) for parent in self.inputs))

class Nor(Gate):
	def __init__(self, in1, in2):
		Gate.__init__(self)
		self.fname = "nor"
		self.func = functions["nor"]
		self.inputs = [in1, in2]

class Nand(Gate):
	def __init__(self, in1, in2):
		Gate.__init__(self)
		self.fname = "nand"
		self.func = functions["nand"]
		self.inputs = [in1, in2]

class Out(Gate):
	def __init__(self, label, in1):
		Gate.__init__(self)
		self.fname = "out"
		self.func = lambda x: x
		self.inputs = [in1]

		self.label = label

		self.node_kwargs["color"] = "green"

class In(Gate):
	def __init__(self, label):
		Gate.__init__(self)
		self.fname = "in"
		self.func = lambda: None
		self.inputs = []

		self.label = label

		self.node_kwargs["color"] = "red"

	def get_value(self, inputs):
		return inputs[self.label]

def get_output(input_values, outputs):
	return {output.label: output.get_value(input_values) for output in outputs}

def boolean_table(inputs, outputs):
	table = np.empty((2**len(inputs), len(inputs)+len(outputs),), dtype=np.bool)
	mesh = np.array(np.meshgrid(*[[False, True] for i in range(len(inputs))], indexing="ij"))
	mesh.shape = len(inputs), 2**len(inputs)
	mesh = mesh.T

	for i in range(2**len(inputs)):
		table[i, :len(inputs)] = mesh[i]
		input_values = {input_names[k]:table[i, k] for k in range(len(inputs))}
		for j, o in enumerate(outputs):
			table[i, j+len(inputs)] = o.get_value(input_values)
	return table

configs = [
	{
		"num_gates":5,
		"stretch_factor":2.5,
		"title":"supereasy",
		"gate_types":[Nor],
		"random_seed":0
	},
	{
		"num_gates":25,
		"stretch_factor":2.5,
		"title":"easy",
		"gate_types":[Nor],
		"random_seed":3
	},
	{
		"num_gates":40,
		"stretch_factor":2.0,
		"title":"medium",
		"gate_types":[Nand],
		"random_seed":1
	},
	{
		"num_gates":70,
		"stretch_factor":3.5,
		"title":"hard",
		"gate_types":[Nor],
		"random_seed":17
	}
]

input_names = ["DRV", "SET", "AVM", "DEL", "XTR", "LVL", "VDS"]
output_names = ["AUX", "SRV", "DXF", "RTS"]

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

		output_integers.append(np.sum(np.power(2, np.arange(num_outputs))[None, :] * output_table, axis=1))

		for i in range(num_outputs):
			print("output {}: {} probability to be True".format(i, np.sum( output_table[:, i]) / (2**num_inputs) ))

		Gate.all_gates = []

	# generate cheatsheet
	with open("cheatsheet.html","w") as f:
		f.write("""<html>\n<head><title>Module: Gates - Cheatsheet</title></head>\n<body>\n""")
		for i, table in enumerate(tables):
			f.write("""<div style="position:absolute;width:{}%;left:{}%;">\n""".format(100//len(tables), 100//len(tables)*i))
			f.write("<p>{}</p>\n".format(configs[i]["title"]))
			f.write("""<table cellborder="1">\n<thead><tr>""")
			for i in input_names:
				f.write("<td>{}</td>".format(i))
			for o in output_names:
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
	pininput = "\n".join(["""
	if(digitalRead(PIN_{name}) == HIGH)
		input_value |= (1<<{bit});
	""".format(name=name, bit=i) for i, name in enumerate(output_names)])

	lookuptable = ",\n".join([
		"// {}\n{{ ".format(configs[i]["title"])+np.array2string(oi, separator=", ")[1:-1]+"}" # remove [] on the outside
		for i, oi in enumerate(output_integers)])

	setup  = "\n".join(["""\tpinMode(PIN_{name}, OUTPUT);""".format(name=name) for name in input_names])
	setup += "\n\n"
	setup += "\n".join(["""\tpinMode(PIN_{name}, INPUT_PULLUP);""".format(name=name) for name in output_names])

	setdisplay = "\n".join(["""\tdigitalWrite(PIN_{name}, random_value & (1<<{bit}) ? HIGH : LOW);""".format(name=name, bit=i) for i, name in enumerate(input_names)])

	with open("autowires.cpp.in", "r") as f:
		template = f.read()

	with open("autowires.cpp","w") as f:
		f.write("// This file has been generated automatically! Do not modify!\n")
		f.write(template.format(
			lookuptable=lookuptable,
			pininput=pininput,
			setup=setup,
			setdisplay=setdisplay,
			num_tables=len(tables),
			num_combinations=len(tables[0])))

	# generate panel svg
	with open("panel.svg", "w") as f:
		cut = "fill:none;stroke:#FF0000;stroke-width:0.1mm"
		engrave = "fill:#00FF00"
		led_radius = 2.5
		switch_radius = 3.0
		button_radius = 4.0

		circle = """<circle style="{style}" cx="{}" cy="{}" r="{}"/>\n"""
		svg_start = """<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" width="{width}{units}" height="{height}{units}" viewBox="{viewBox}" id="{id}" version="1.1">\n""".format(
			width=100, height=100, id="panel", units="mm", viewBox="0 0 100 100")
		svg_end = "</svg>\n"
		text = """<text x="{}" y="{}" font-family="monospace" text-anchor="middle" font-size="6" style="{style}">{}</text>\n"""

		names = input_names+output_names
		random.shuffle(names)

		f.write(svg_start)

		num_cols = 4
		num_rows = 3

		h_padding = 15.0
		v_padding = 15.0

		text_offset = - 6.0

		h_distance = (100.0 - 2*h_padding)/(num_cols-1)
		v_distance = (100.0 - 2*v_padding)/(num_rows-1)

		for i, name in enumerate(names):
			x = i // num_rows * h_distance + h_padding
			y = i %  num_rows * v_distance + v_padding
			radius = led_radius if name in input_names else switch_radius

			f.write(circle.format(x, y, radius, style=cut))
			f.write(text.format(x, y+text_offset, name, style=engrave))

		x = (num_cols-1) * h_distance + h_padding
		y = (num_rows-1) * v_distance + v_padding

		f.write(circle.format(x, y, button_radius, style=cut))
		f.write(text.format(x, y+text_offset, "RUN", style=engrave))



		f.write(svg_end)
	
	# generate manual figures
	with open("manual_figures.tex", "w") as f:
		for i, config in enumerate(configs):
			f.write(r"""
			\begin{{figure}}[h]
				\begin{{center}}
				\includegraphics[scale=0.4]{{wires_{i}}}
				\caption{{Internal wiring for series {title}}}
				\end{{center}}
			\end{{figure}}""".format(i=i, title=config["title"]))

if __name__ == "__main__":
	main()

