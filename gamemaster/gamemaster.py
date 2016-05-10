#!/usr/bin/python3
import argparse
import random
import time

import Bus

BAUDRATE = 38400

# parse arguments
parser = argparse.ArgumentParser(description="BUMM Gamemaster")
parser.add_argument("serial_device", type=str, help="Serial device used for bus communication")
parser.add_argument("num_modules", type=int, help="Number of active modules")
parser.add_argument("difficulty", type=int, help="Difficulty value from 0-255")
parser.add_argument("time", type=int, help="Number of seconds for the countdown timer")
parser.add_argument("max_errors", type=int, default=0, help="Maximum errors allowed")
parser.add_argument("--disable", type=str, nargs="?", default="", const="", help="Comma separated list of disabled modules")
main_args = parser.parse_args()

bus = Bus.Bus(main_args.serial_device, BAUDRATE)

def check_argument_validity(args):
	assert 0 <= args.difficulty <= 255
	assert args.time > 0
	assert args.max_errors >= 0
	for m in args.disable.split(","):
		assert isinstance(m, str)
		assert len(m) == 1

def check_existing_modules():
	result = []
	print("found the following modules")
	print("---+-----------")
	print("   | revision  ")
	print("---+-----------")
	for m in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789":
		revision = bus.check_for_module(m)
		if revision is not None:
			print(" {} | {}".format(m, revision))
			result.append(m)
	return result

def explode():
	print("BOOOM!")

def win():
	print("BOMB HAS BEEN DEFUSED!")

def start(args):
	modules = check_existing_modules()
	available_modules = [m for m in modules if m not in args.disable.split(",")]
	used_modules = random.sample(available_modules, args.num_modules)

	for m in modules:
		bus.init_module(m, m in used_modules, args.difficulty)

	time.sleep(10) # wait for potential hardware reset
	bus.start_game()

	explosion_time = time.clock() + args.time

	while True:
		total_failures = 0
		defused = 0
		for m in used_modules:
			success, num_failures = bus.poll_status(m)
			total_failures += num_failures
			if success:
				defused += 1
		time_left = int(explosion_time - time.clock())
		bus.broadcast_status(time_left, num_failures)
		print(time_left)

		if time_left <= 0 or num_failures > args.max_errors:
			explode()
			break

		if defused == args.num_modules:
			win()
			break

start(main_args)
