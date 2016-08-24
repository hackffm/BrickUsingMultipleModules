#!/usr/bin/python3
import math
import sys
sys.path.append("../../parts")
sys.path.append("../common/layout_generation")
import top_plate
import layout

with open("layout_autogen.tex","w") as f:
	f.write(layout.make_plate())

	objects = (
		("green control led", top_plate.plate_width*1/4, top_plate.plate_height*1/3, top_plate.plate_height*4/9.0, "led_off"),
		("red control led", top_plate.plate_width*3/4, top_plate.plate_height*1/3, top_plate.plate_height*3/9.0, "led_off"),
		("green input button", top_plate.plate_width*1/4, top_plate.plate_height*2/3, top_plate.plate_height*5/9.0, "led_off"),
		("red input button", top_plate.plate_width*3/4, top_plate.plate_height*2/3, top_plate.plate_height*6/9.0, "led_off"),
	)

	for label, x, y, label_y, clipart in objects:
		f.write(layout.make_clipart((x, y), clipart))
		f.write(layout.make_label((x, y), label, label_y=label_y))

