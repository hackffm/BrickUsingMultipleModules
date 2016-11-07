#!/usr/bin/python3
import pickle
import random
import config

random.seed(0)

with open("lookuptable_autogen.dat", "rb") as f:
	lookuptable = pickle.load(f)


table_columns = 8

with open("manual_tables_autogen.tex", "w") as f:
	for i_set, params in enumerate(config.parameters):
		f.write(r"\begin{table}\begin{center}\begin{tabular}{|cccccccc|}\hline"+"\n")
		strings = []
		for i, result in enumerate(lookuptable[i_set]):
			blink_string = "".join("r" if i & (1<<j) else "g" for j in range(params["num_blinks"]))[::-1]
			strings.append( blink_string + result )
		if not params["show_ordered_in_manual"]:
			random.shuffle(strings)

		for i, string in enumerate(strings):
			separator = " \\\\\n" if (i % table_columns) == (table_columns-1) else " & "
			f.write(string + separator)

		caption = "\en{{Codebook for modules from {0}xxx to {1}xxx}}\de{{Codebuch für Module von {0}xxx bis {1}xxx}}".format(*params["difficulty_interval"])
		f.write(r"\hline\end{{tabular}}\end{{center}}\caption{{{}}}\end{{table}}".format(caption)+"\n\n")
