#!/usr/bin/python3
import math
from common import *
import sys
sys.path.append("../../parts")
sys.path.append("../common/layout_generation")
import top_plate
import layout

with open("layout_autogen.tex","w") as f:
	names = ["SET", "DEL", "RTS", "AUX", "AVM", "XTR", "DRV", "DXF", "VDS", "SRV", "LVL", "RUN"]

	num_cols = 4
	num_rows = 3

	h_padding = 15.0
	v_padding = 30.0

	h_distance = (100.0 - 2*h_padding)/(num_cols-1)
	v_distance = (100.0 - 2*v_padding)/(num_rows-1)

	f.write(layout.make_plate())

	for i, name in enumerate(names):
		x_i = i // num_rows
		y_i = i % num_rows
		x = x_i * h_distance + h_padding
		y = y_i * v_distance + v_padding

		if name in output_names:
			f.write(layout.make_clipart((x,y), "switch_up"))
		else:
			f.write(layout.make_clipart((x,y), "led_off"))

		f.write(layout.make_label((x, y), name, "left" if x_i in (0,1) else "right", y-v_distance*{0:0, 1:-0.5, 2:+0.5, 3:0}[x_i]))

