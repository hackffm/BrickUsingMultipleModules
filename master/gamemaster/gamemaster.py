#!/usr/bin/python2
import argparse
import random
import time

import Bus
from Sound import SoundManager

BAUDRATE = 19200

# parse arguments
parser = argparse.ArgumentParser(description="BUMM Gamemaster")
parser.add_argument("serial_device", type=str, help="Serial device used for bus communication")
parser.add_argument("num_modules", type=int, help="Number of active modules")
parser.add_argument("difficulty", type=int, help="Difficulty value from 10-99")
parser.add_argument("time", type=int, help="Number of seconds for the countdown timer")
parser.add_argument("max_errors", type=int, default=0, help="Maximum errors allowed")
parser.add_argument("--disable", metavar="module", type=str, nargs="+", default="", help="Disable (don't use) the specified modules")
parser.add_argument("--ignore-control-module", action="store_true", help="Do not wait for OK from control module. Makes testing easier.")

def linspace(start, stop, step):
	return list(i*step for i in range( int(start/step), int(stop/step) ) )

def make_beep_times(fulltime):
	result = ( linspace(0, 5, 0.2) + linspace(5, 10, 0.5) + linspace(10, 20, 1) + linspace(20, fulltime, 5) )[::-1]
	print(result)
	return result

def check_argument_validity(args):
	assert 10 <= args.difficulty <= 99
	assert args.time > 0
	assert args.max_errors >= 0
	for m in args.disable:
		assert len(m) == 1

def check_existing_modules(bus):
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


def start(args, bus):
	sound = SoundManager({"beep":"beep_short.wav", "beep_end": "beep_end.wav"})
	serial_number = str(args.difficulty) + str(random.randrange(0, 99)).zfill(2) + chr(0x41+random.randrange(0,26))
	print("serial number: {}".format(serial_number))

	# check for control panel
	if not args.ignore_control_module:
		control_description = bus.check_for_module(Bus.CONTROL_MODULE)
		if control_description is None:
			raise Exception("no control module found!")
		bus.init_module(Bus.CONTROL_MODULE, True, serial_number, control_description["num_random"])

	# check other modules
	modules = check_existing_modules(bus)
	available_modules = [m for m in modules if m not in args.disable.split(",")]
	used_modules = random.sample(available_modules, args.num_modules)

	# init all normal modules
	for m in modules:
		bus.init_module(m, m in used_modules, serial_number, modules[m]["num_random"])

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
	beeptimes = make_beep_times(args.time)
	next_beep_index = 0

	last_time_left = args.time
	last_num_lifes = args.max_errors

	while True:
		num_lifes = args.max_errors
		defused = 0
		for m in used_modules:
			success, module_failures = bus.poll_status(m)
			num_lifes -= module_failures
			if success:
				defused += 1

		if num_lifes < 0:
			num_lifes = 0

		# make countdown sounds
		if ( explosion_time - time.time() ) < sound["beep_end"].get_length():
			sound["beep_end"].play()
		elif ( explosion_time - time.time() ) < beeptimes[next_beep_index]:
			next_beep_index += 1
			sound["beep"].play()

		time_left = int(explosion_time - time.time())

		if last_time_left != time_left or last_num_lifes != num_lifes:
			bus.broadcast_status(time_left, num_lifes)
			last_time_left = time_left
			last_num_lifes = num_lifes


		print(time_left)

		if time_left <= 0:
			bus.end_game(1)
			explode()
			break
		if num_lifes == 0:
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

