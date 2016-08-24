#!/usr/bin/python3
import sys
import pickle
import config

with open("lookuptable_autogen.dat", "rb") as f:
	lookuptable = pickle.load(f)

def get_set_number(serial):
	difficulty = int(serial[0:2])
	for i, params in enumerate(config.parameters):
		if params["difficulty_interval"][0] <= difficulty < params["difficulty_interval"][1]:
			return i
	raise Exception("no parameters defined for difficulty {}!!".format(difficulty))

def cap_ints(serial, randomness):
	set_number = get_set_number(serial)
	return [randomness[i] % 2**config.parameters[set_number]["num_blinks"] for i in range(config.parameters[set_number]["num_rounds"])]

def get_command_chars(serial, randomness):
	display_ints = cap_ints(serial, randomness)
	return [lookuptable[get_set_number(serial)][i] for i in display_ints]

def describe(serial, randomness):
	display_ints = cap_ints(serial, randomness)
	num_blinks = config.parameters[get_set_number(serial)]["num_blinks"]
	return " - ".join(
		"".join(
			"r" if display_int & (1<<j) else "g"
			for j in range(num_blinks)
		)[::-1]
		for display_int in display_ints)

def hints(serial, randomness):
	return " ".join(get_command_chars(serial, randomness))

def solution(serial, randomness):
	values = []
	for command_number, cmd in enumerate(get_command_chars(serial, randomness)):
		values.append(eval(config.button_modes[cmd]["solver"]))
	return " ".join("R" if value else "G" for value in values)

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
	
	print(cmd(serial, randomness))

main()
