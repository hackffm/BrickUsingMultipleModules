import math
import sys
sys.path.append("../../parts")
import top_plate

margin = 20
connector_distance = 6

left_x = 0 - margin
right_x = top_plate.plate_width + margin
sqhalf = math.sqrt(0.5)


running_number = 1
def get_running_number():
	global running_number
	running_number += 1
	return running_number

def make_clipart(position, clipart, name=None):
	assert isinstance(position, tuple) and len(position) == 2
	if name is None:
		name = get_running_number()

	return r"\node ({}) at ({},{}) {{\includegraphics{{../common/cliparts/{}}}}};".format(name, position[0], position[1], clipart)

def make_plate():
	return r"\draw [thick] (0,0) -- ({0},0) -- ({0},{1}) -- (0,{1}) -- (0,0);".format(top_plate.plate_width, top_plate.plate_width)

def make_label(position, label, label_horizontal="right", label_y="same"):
	assert label_horizontal in ("left", "right")

	x, y = position
	if label_y == "same":
		label_y = y

	label_x = dict(left=left_x, right=right_x)[label_horizontal]
	leftrightfactor = dict(left=1, right=-1)[label_horizontal]
	topdownfactor = 0 if label_y == y else (1 if label_y > y else -1)

	kink_point_offset = max(math.fabs(label_y - y), connector_distance)
	coordinates = (
		(label_x, label_y), # label point
		(x - kink_point_offset*leftrightfactor, y+kink_point_offset*topdownfactor), # kink point
		(x - connector_distance*(1.0 if label_y == y else sqhalf)*leftrightfactor, y+connector_distance*sqhalf*topdownfactor) # "arrowhead"
	)
	result = ""
	result += r"\draw [ultra thin] {};".format(" -- ".join("({},{})".format(*c) for c in coordinates))
	result += r"\node [{}] at ({},{}) {{{}}};".format(label_horizontal, coordinates[0][0], coordinates[0][1], label)
	return result

