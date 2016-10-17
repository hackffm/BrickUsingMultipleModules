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
	rect = """<rect style="{style}" width="{w}" height="{h}" x="{x}" y="{y}"/>\n"""
	svg_start = """<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" width="{width}{units}" height="{height}{units}" viewBox="0 0 {width} {height}" id="{id}" version="1.1">\n""".format(
		width=top_plate.plate_width, height=top_plate.plate_width, id="panel", units="mm")
	svg_end = "</svg>\n"
	text = """<text x="{}" y="{}" font-family="monospace" text-anchor="middle" font-size="6" style="{style}">{}</text>\n"""

	f.write(svg_start)

	f.write(top_plate.make_top_plate("lt rt lb rb"))

	#f.write(circle.format(top_plate.plate_width/2, -top_plate.hole_distance, laser_config.radius_led5, style=cut))

	available_width = (top_plate.plate_width + 2*top_plate.hole_distance)

	distance_x = 10.0
	life_led_y = 30.0

	timer_width = 50.3
	timer_height = 19.0
	timer_y_center = top_plate.plate_height/2

	for i in range(-3, 4):
		f.write(circle.format( (top_plate.plate_width)/2 + i*distance_x , life_led_y, laser_config.radius_led5, style=cut))
	
	f.write(rect.format(h=timer_height, w=timer_width, y=timer_y_center-timer_height/2, x=top_plate.plate_width/2-timer_width/2, style=cut))

	f.write(svg_end)

with open("panel_autogen_recttest.svg", "w") as f:
	f.write(svg_start)
	f.write(rect.format(h=timer_height, w=timer_width, y=timer_y_center-timer_height/2, x=top_plate.plate_width/2-timer_width/2, style=cut))
	f.write(svg_end)
