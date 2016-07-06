#!/usr/bin/python3
import pickle
from common import *

def main():
	num_inputs = len(input_names)
	num_outputs = len(output_names)

	gates_per_config = []

	for config_number, config in enumerate(configs):
		random.seed(config["random_seed"])


		num_gates = config["num_gates"]
		stretch_factor = config["stretch_factor"]

		inputs = []
		intermediate_gates = []
		outputs = []
		gates = []

		for i in range(num_inputs):
			inputs.append(In(input_names[i]))
		gates += inputs

		for i in range(num_gates):
			gate_type = random.choice(config["gate_types"])
			gate = gate_type(*random.sample(gates[-int(num_inputs*stretch_factor):], 2))
			intermediate_gates.append(gate)
			gates.append(gate)


		for i in range(num_outputs):
			outputs.append(Out(output_names[i], intermediate_gates[-(i+1)]))
		gates += outputs

		# prune graph
		continue_pruning = True
		while(continue_pruning):
			continue_pruning = False
			for gate in gates:
				gate.has_children = gate in outputs

			for gate in gates:
				for parent in gate.inputs:
					parent.has_children = True
			rest = [gate for gate in gates if gate.has_children]
			if len(rest) < len(gates):
				gates[:] = rest
				continue_pruning = True

		gates_per_config.append(gates)
	
	with open(GATE_FILE, "wb") as f:
		pickle.dump(gates_per_config, f)

main()
