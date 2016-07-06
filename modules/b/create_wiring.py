#!/usr/bin/python3
import sys
import random
import pickle
import numpy as np

from common import *

def get_output(input_values, outputs):
	return {output.label: output.get_value(input_values) for output in outputs}



def main():
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

if __name__ == "__main__":
	main()
