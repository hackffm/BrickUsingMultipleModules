#!/usr/bin/python3
import argparse
import random
import time

import Bus

BAUDRATE = 19200

# parse arguments
parser = argparse.ArgumentParser(description="BUMM Gamemaster")
parser.add_argument("serial_device", type=str, help="Serial device used for bus communication")
parser.add_argument("num_modules", type=int, help="Number of active modules")
parser.add_argument("difficulty", type=int, help="Difficulty value from 0-255")
parser.add_argument("time", type=int, help="Number of seconds for the countdown timer")
parser.add_argument("max_errors", type=int, default=0, help="Maximum errors allowed")
parser.add_argument("--disable", metavar="module", type=str, nargs="+", default="", help="Disable (don't use) the specified modules")
parser.add_argument("--ignore-control-module", action="store_true", help="Do not wait for OK from control module. Makes testing easier.")

def check_argument_validity(args):
	assert 0 <= args.difficulty <= 255
	assert args.time > 0
	assert args.max_errors >= 0
	for m in args.disable:
		assert len(m) == 1

def check_existing_modules():
	result = {}
	print("found the following modules")
	print("---+-----------")
	print("   | revision  ")
	print("---+-----------")
	for m in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789":
		description = bus.check_for_module(m)
		if description is not None:
			print(" {} | {}".format(m, description["revision"]))
			result[m] = description
	return result

def explode():
	print("BOOOM!")

def win():
	print("BOMB HAS BEEN DEFUSED!")

def make_sound(name):
	pass

def start(args, bus):
	# check for control panel
	if not args.ignore_control_module:
		control_description = bus.check_for_module(Bus.CONTROL_MODULE)
		if control_description is None:
			raise Exception("no control module found!")
		bus.init_module(Bus.CONTROL_MODULE, True, args.difficulty, control_description["num_random"])

	# check other modules
	modules = check_existing_modules(bus)
	available_modules = [m for m in modules if m not in args.disable.split(",")]
	used_modules = random.sample(available_modules, args.num_modules)

	# init all normal modules
	for m in modules:
		bus.init_module(m, m in used_modules, args.difficulty, modules[m]["num_random"])

	# wait for start switch on control panel
	if not args.ignore_control_module:
		bus.start_game(Bus.CONTROL_MODULE)
		while(True):
			continue_waiting, _ = bus.poll_status(Bus.CONTROL_MODULE)
			if not continue_waiting:
				break
	else:
		print("waiting 5s for game start...")
		time.sleep(5)
	
	for m in used_modules:
		bus.start_game(m)
	explosion_time = time.time() + args.time

	last_time_left = args.time
	last_num_failures = 0

	while True:
		num_failures = 0
		defused = 0
		for m in used_modules:
			success, module_failures = bus.poll_status(m)
			num_failures += module_failures
			if success:
				defused += 1

		time_left = int(explosion_time - time.time())
		
		# make countdown sounds
		if last_time_left != time_left:
			if time_left < 20 or time_left % 10 == 0: # make beep every 10s or every second during last 20
				make_sound("beep")

		if last_time_left != time_left or last_num_failures != num_failures:
			bus.broadcast_status(time_left, num_failures)
			last_time_left = time_left
			last_num_failures = num_failures


		print(time_left)

		if time_left <= 0:
			bus.end_game(1)
			explode()
			break
		if num_failures > args.max_errors:
			bus.end_game(2)
			explode()
			break

		if defused == args.num_modules:
			bus.end_game(0)
			win()
			break

def main():
	main_args = parser.parse_args()

	bus = Bus.Bus(main_args.serial_device, BAUDRATE)
	start(main_args, bus)

if __name__=="__main__":
	main()

