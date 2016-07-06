import random

GATE_FILE = "gates_autogen.dat"
TABLE_FILE = "lookuptable_autogen.npy"

class Gate(object):
	running_number = 0
	all_gates = []
	def __init__(self):
		self.number = Gate.running_number
		Gate.running_number += 1
		Gate.all_gates.append(self)
		self.label = None

		self.children = False

		self.node_kwargs = {"fontname":"Courier"}

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
		self.inputs = [in1, in2]

	def func(self, a, b):
		return not (a or b)

class Nand(Gate):
	def __init__(self, in1, in2):
		Gate.__init__(self)
		self.fname = "nand"
		self.inputs = [in1, in2]
	
	def func(self, a, b):
		return not (a and b)

class Out(Gate):
	def __init__(self, label, in1):
		Gate.__init__(self)
		self.fname = "out"
		self.inputs = [in1]

		self.label = label

		self.node_kwargs["color"] = "green"
	
	def func(self, a):
		return a

class In(Gate):
	def __init__(self, label):
		Gate.__init__(self)
		self.fname = "in"
		self.inputs = []

		self.label = label

		self.node_kwargs["color"] = "red"

	def get_value(self, inputs):
		return inputs[self.label]
	
	def func(self):
		return None

# IMPORTANT: remember to change serialnumber->lookuptable-index in b.ino AND in module_solver.py!
configs = [
	{
		"num_gates":5,
		"stretch_factor":2.5,
		"title":"10xxx-19xxx",
		"gate_types":[Nor],
		"random_seed":0
	},
	{
		"num_gates":25,
		"stretch_factor":2.5,
		"title":"20xxx-39xxx",
		"gate_types":[Nor],
		"random_seed":3
	},
	{
		"num_gates":40,
		"stretch_factor":2.0,
		"title":"40xxx-59xxx",
		"gate_types":[Nand],
		"random_seed":1
	},
	{
		"num_gates":70,
		"stretch_factor":3.5,
		"title":"60xxx and later",
		"gate_types":[Nor],
		"random_seed":17
	}
]

random.seed(0)
switch_inverts = sorted(random.sample( [str(i)+str(j) for i in range(0,10) for j in range(0,10)] , 30)) # number of inverted switches has to be a multiple of 5!
led_inverts = sorted(random.sample([chr(0x41+i) for i in range(26)], 5))

input_names = ["DRV", "SET", "AVM", "DEL", "XTR", "LVL", "VDS"]
output_names = ["AUX", "SRV", "DXF", "RTS"]


