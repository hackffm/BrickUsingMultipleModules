from laser_config import styles, radius_m4

plate_width = 100.0
plate_height = plate_width
hole_distance = -6.0
plate_padding = 5.0

total_width = plate_width + plate_padding
total_height = plate_height + plate_padding

left = -hole_distance
right = plate_width + hole_distance
xmiddle = plate_width/2
top = -hole_distance
bottom = plate_height + hole_distance
ymiddle = plate_height/2

positions = {
	"l": (left, ymiddle),
	"lt": (left, top),
	"t": (xmiddle, top),
	"rt": (right, top),
	"r": (right, ymiddle),
	"rb": (right, bottom),
	"b": (xmiddle, bottom),
	"lb": (left, bottom)
}

# position_flags: space separated string of the following flags: l t r b lt lb rt rb (right, left, top, bottom)
def make_top_plate(position_flags):
	svg_code = ""
	for posname in position_flags.split(" "):
		try:
			position = positions[posname]
		except KeyError:
			raise Exception("position {} not found! Possible values: {}".format(posname, " ".join(positions.keys())))
		svg_code += """<circle style="{}" cx="{}" cy="{}" r="{}"/>\n""".format(styles["cut"], position[0], position[1], radius_m4)
	p = plate_padding
	svg_code += """<path style="{}" d="M {} {} L {} {} L {} {} L {} {} L {} {}" />""".format(styles["cut"],
			-p, -p,
			plate_width+p, -p,
			plate_width+p, plate_height+p,
			-p, plate_height+p,
			-p, -p
			)
	return svg_code

if __name__ == "__main__":
	import sys
	try:
		target = sys.argv[1]
		position_flags = sys.argv[2]
	except IndexError:
		sys.exit('USAGE example: {} target.svg "lt rt"'.format(sys.argv[0]))
	
	svg_start = """<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" width="{width}{units}" height="{height}{units}" viewBox="0 0 {width} {height}" id="{id}" version="1.1">\n""".format(width=plate_width, height=plate_height, id="panel", units="mm")
	svg_end = "</svg>\n"
	content = make_top_plate(position_flags)

	with open(target, "w") as f:
		f.write(svg_start)
		f.write(content)
		f.write(svg_end)
