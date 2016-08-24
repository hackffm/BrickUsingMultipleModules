#!/usr/bin/python3
import pickle
import config

with open("lookuptable_autogen.dat", "rb") as f:
	lookuptable = pickle.load(f)

with open("d.ino.in", "r") as f:
	template = f.read()

max_rounds = max(p["num_rounds"] for p in config.parameters)

#num_tables = len(config.parameters)

#masks = ", ".join(str(2**p["num_blinks"]-1) for p in config.parameters)

lookuptables = "\n".join("const uint8_t PROGMEM lookuptable_{}[] = {{ '{}' }};".format(i, "', '".join(table)) for i, table in enumerate(lookuptable))

init_patterns = "\n".join("""
	if( ( {} <= difficulty ) && (difficulty < {}) )
	{{
		current_pattern_length = {};
		num_iterations = {};
		ICR1 = {};
		OCR1A = {};
	}}
	""".format(p["difficulty_interval"][0], p["difficulty_interval"][1], p["num_blinks"], p["num_rounds"], 16*p["blink_speed"], int(16*p["blink_speed"]*0.2)) for i, p in enumerate(config.parameters))

difficulty_chooser = "\n".join("""
	if( ( {} <= difficulty ) && (difficulty < {}) )
	{{
		return pgm_read_byte(lookuptable_{}+number);
	}}
	""".format(p["difficulty_interval"][0], p["difficulty_interval"][1], i) for i, p in enumerate(config.parameters))

check_commands = "\n".join("""
	case '{}':
	{{
		return {};
	}}break;
	""".format(key, value["code"]) for key, value in config.button_modes.items())

result = template % (max_rounds, lookuptables, init_patterns, difficulty_chooser, check_commands)

with open("d_autogen.ino", "w") as f:
	f.write("// This file has been generated automatically! Do not modify!\n")
	f.write(result)
