import pickle
import pygraphviz as pgv
from common import *

def main():
	with open(GATE_FILE, "rb") as f:
		gates_per_config = pickle.load(f)
	
	for config_number, config in enumerate(configs):
		gates = gates_per_config[config_number]
		g = pgv.AGraph(directed=True)

		for gate in gates:
			gate.put_to_graph(g)

		g.layout(prog='dot')
		g.draw("wires_{}.pdf".format(config_number))

main()
