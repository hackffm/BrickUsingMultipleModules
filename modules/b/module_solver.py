#!/usr/bin/python3

import sys
import common
import numpy as np

def describe(serial, randomness):
	invert_leds = serial[4] in common.led_inverts

	result = ", ".join("{} : {}".format(name, "on" if (((randomness[0] & 1<<i) != 0) != invert_leds) else "off") for i, name in enumerate(common.input_names))

	return result

def hints(serial, randomness):
	invert_leds = serial[4] in common.led_inverts
	invert_switches = serial[2:4] in common.switch_inverts

	led_string = "leds INVERTED" if invert_leds else "leds normal"
	switch_string = "switches INVERTED" if invert_switches else "switches normal"

	return "{}, {}".format(led_string, switch_string)

def solution(serial, randomness):
	invert_switches = serial[2:4] in common.switch_inverts
	table = np.load(common.TABLE_FILE)

	if(serial[0] < '2'):
		difficulty_index = 0
	elif(serial[0] < '4'):
		difficulty_index = 1
	elif(serial[0] < '6'):
		difficulty_index = 2
	else:
		difficulty_index = 3

	switch_states = table[difficulty_index, randomness[0], len(common.input_names):]

	result = ", ".join("{}: {}".format(name, "down" if switch_states[-i-1] != invert_switches else "up") for i, name in enumerate(common.output_names))

	return result

commands = {"describe": describe, "hints": hints, "solution": solution}

def main():
	try:
		command, serial = sys.argv[1:3]
		randomness = [int(i) for i in sys.argv[3:]]
	except ValueError:
		sys.exit("USAGE: {} command serial random_numbers".format(sys.argv[0]))

	try:
		cmd = commands[command]
	except KeyError:
		sys.exit("available commands: {}".format(", ".join(commands)))
	
	assert len(randomness) == 1

	print(cmd(serial, randomness))

main()
