#!/usr/bin/python3
import sys
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

	f.write(svg_start)

	f.write(top_plate.make_top_plate("lt rt lb rb"))

	f.write(circle.format(top_plate.plate_width/2, -top_plate.hole_distance, laser_config.radius_led5, style=cut))

	available_width = (top_plate.plate_width + 2*top_plate.hole_distance)
	distance_x = available_width / 2.0
	distance_y = available_width / 3.0

	f.write(circle.format( (top_plate.plate_width+distance_x)/2 , (top_plate.plate_height-distance_y)/2, laser_config.radius_led5, style=cut))
	f.write(circle.format( (top_plate.plate_width-distance_x)/2 , (top_plate.plate_height-distance_y)/2, laser_config.radius_led5, style=cut))

	f.write(circle.format( (top_plate.plate_width-distance_x)/2 , (top_plate.plate_height+distance_y)/2, laser_config.radius_button_small, style=cut))
	f.write(circle.format( (top_plate.plate_width+distance_x)/2 , (top_plate.plate_height+distance_y)/2, laser_config.radius_button_small, style=cut))

	f.write(svg_end)

