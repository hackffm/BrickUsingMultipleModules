#!/usr/bin/python3
import math
from common import *
import sys
sys.path.append("../../parts")
import top_plate

with open("layout_autogen.tex","w") as f:
	names = ["SET", "DEL", "RTS", "AUX", "AVM", "XTR", "DRV", "DXF", "VDS", "SRV", "LVL", "RUN"]

	num_cols = 4
	num_rows = 3

	h_padding = 15.0
	v_padding = 30.0

	text_offset = - 6.0

	h_distance = (100.0 - 2*h_padding)/(num_cols-1)
	v_distance = (100.0 - 2*v_padding)/(num_rows-1)
	sq2 = math.sqrt(2)

	f.write(r"\draw [thick] (0,0) -- ({0},0) -- ({0},{1}) -- (0,{1}) -- (0,0);".format(top_plate.plate_width, top_plate.plate_width))

	for i, name in enumerate(names):
		x_i = i // num_rows
		y_i = i % num_rows
		x = x_i * h_distance + h_padding
		y = y_i * v_distance + v_padding

		radius = 3 #laser_config.radius_led5 if name in input_names else laser_config.radius_switch

		if name in output_names:
			f.write(r"\node ({}) at ({},{}) {{\includegraphics{{../common/cliparts/switch_up}}}};".format(name, x, y))
		else:
			f.write(r"\node ({}) at ({},{}) {{\includegraphics{{../common/cliparts/led_off}}}};".format(name, x, y))

		margin = 20

		left_x = 0 - margin
		right_x = top_plate.plate_width + margin

		if x_i == 0:
			coordinates = ((left_x, y), (x-sq2*radius, y))
		elif x_i == 1:
			coordinates = ((left_x, y+0.5*v_distance), (x-0.5*v_distance, y+0.5*v_distance), (x-radius, y+radius) )
		elif x_i == 2:
			coordinates = ((right_x, y-0.5*v_distance), (x+0.5*v_distance, y-0.5*v_distance), (x+radius, y-radius) )
		elif x_i == 3:
			coordinates = ((right_x, y), (x+sq2*radius, y))
		else:
			coordinates = ()
		f.write(r"\draw [ultra thin] {};".format( " -- ".join("({},{})".format(*c) for c in coordinates) ))
		f.write(r"\node [{}] at ({},{}) {{{}}};".format("left" if x_i in (0,1) else "right", coordinates[0][0], coordinates[0][1], name))

