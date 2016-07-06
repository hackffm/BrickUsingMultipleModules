import pickle
import numpy as np

from common import *

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

main()
