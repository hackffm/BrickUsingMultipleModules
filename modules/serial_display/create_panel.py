#!/usr/bin/python3
import sys
sys.path.append("../../parts")
import top_plate
import laser_config

# generate panel svg
with open("panel_autogen.svg", "w") as f:
	cut = laser_config.styles["cut"]
	engrave = laser_config.styles["engrave"]

	svg_start = """<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" width="{width}{units}" height="{height}{units}" viewBox="0 0 {width} {height}" id="{id}" version="1.1">\n""".format(
		width=top_plate.plate_width, height=top_plate.plate_width, id="panel", units="mm")
	svg_end = "</svg>\n"
	rect = """<rect style="{style}" width="{w}" height="{h}" x="{x}" y="{y}"/>\n"""
	text = """<text x="{}" y="{}" font-family="monospace" text-anchor="middle" font-size="6" style="{style}">{}</text>\n"""
	f.write(svg_start)

	display_width = 72.0
	display_height = 32.0
	display_y_center = top_plate.plate_width/2

	f.write(top_plate.make_top_plate("lt rt lb rb"))
	f.write(rect.format(h=display_height, w=display_width, y=display_y_center-display_height/2, x=top_plate.plate_width/2-display_width/2, style=cut))

	f.write(svg_end)

