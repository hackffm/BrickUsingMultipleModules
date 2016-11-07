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
		("\en{green control led}\de{grüne Nachrichtenleuchte}", top_plate.plate_width*1/4, top_plate.plate_height*1/3, top_plate.plate_height*4/9.0, "led_off"),
		("\en{red control led}\de{rote Nachrichtenleuchte}", top_plate.plate_width*3/4, top_plate.plate_height*1/3, top_plate.plate_height*3/9.0, "led_off"),
		("\en{green input button}\de{grüner Eingabeknopf}", top_plate.plate_width*1/4, top_plate.plate_height*2/3, top_plate.plate_height*5/9.0, "led_off"),
		("\en{red input button}\de{roter Eingabeknopf}", top_plate.plate_width*3/4, top_plate.plate_height*2/3, top_plate.plate_height*6/9.0, "led_off"),
	)

	for label, x, y, label_y, clipart in objects:
		f.write(layout.make_clipart((x, y), clipart))
		f.write(layout.make_label((x, y), label, label_y=label_y))

