import numpy as np
from common import *

template_pininput = """
	if(digitalRead(PIN_{name}) == HIGH)
		input_value |= (1<<{bit});
"""

def main():
	num_inputs = len(input_names)
	num_outputs = len(output_names)
	tables = np.load(TABLE_FILE)

	pininput = "\n".join([template_pininput.format(name=name, bit=i) for i, name in enumerate(output_names)])
	pininput += "\n\tif(invert_switches(serial_number))\n\t\tinput_value ^= {};\n".format(2**num_outputs-1)

	lookuptable = ",\n".join([
		"// {}\n{{ ".format(configs[i]["title"])+np.array2string(np.sum(np.power(2, np.arange(num_outputs))[None, ::-1] * tables[i, :, num_inputs:], axis=1), separator=", ")[1:-1]+"}" # remove [] on the outside
		for i in range(len(configs))])

	setup  = "\n".join(["""\tpinMode(PIN_{name}, OUTPUT);""".format(name=name) for name in input_names])
	setup += "\n\n"
	setup += "\n".join(["""\tpinMode(PIN_{name}, INPUT_PULLUP);""".format(name=name) for name in output_names+["RUN"]])

	setdisplay = "\tif(invert_leds(serial_number))\n\t\trandom_value ^= 0xFF;\n\n"
	setdisplay += "\n".join(["""\tdigitalWrite(PIN_{name}, random_value & (1<<{bit}) ? HIGH : LOW);""".format(name=name, bit=i) for i, name in enumerate(input_names)])

	invert_leds_string = "\n".join(("""\tif(serial_number[4]=='{}') return 1;""".format(l) for l in led_inverts))

	invert_switches_string = "\n".join(("""\tif( (serial_number[2]=='{}') && (serial_number[3]=='{}') ) return 1;""".format(s[0], s[1]) for s in switch_inverts))

	random_value_bitmask = 2**num_inputs-1

	with open("autowires.cpp.in", "r") as f:
		template = f.read()

	with open("wires_autogen.cpp","w") as f:
		f.write("// This file has been generated automatically! Do not modify!\n")
		f.write(template.format(
			lookuptable=lookuptable,
			pininput=pininput,
			setup=setup,
			setdisplay=setdisplay,
			invert_switches = invert_switches_string,
			invert_leds = invert_leds_string,
			random_value_bitmask = random_value_bitmask,
			num_tables=len(tables),
			num_combinations=len(tables[0])))

main()
