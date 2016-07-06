#!/usr/bin/python3
import sys
from common import *
sys.path.append("../../parts")
import top_plate
import laser_config

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

