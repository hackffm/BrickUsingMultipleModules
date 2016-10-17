#!/usr/bin/python2
import argparse
import random
import time
import sys

import Bus
from Sound import SoundManager
sys.path.append("../lib")
from server import Server
from parse_errorcode_from_cpp import parse_errorcode_from_cpp

BAUDRATE = 19200

# parse arguments
parser = argparse.ArgumentParser(description="BUMM Gamemaster")
parser.add_argument("serial_device", type=str, help="Serial device used for bus communication")
parser.add_argument("--disable", metavar="module", type=str, default="", help="Disable (don't use) the specified modules (unseparated list e.g. 'ac')")

subparsers = parser.add_subparsers(title="modes", description="Pick one of the following modes how to control game flow", dest="mode")

parser_standalone = subparsers.add_parser("standalone", help="directly start a game without control module or gui")

parser_standalone.add_argument("num_modules", type=int, help="Number of active modules")
parser_standalone.add_argument("difficulty", type=int, help="Difficulty value from 10-99")
parser_standalone.add_argument("time", type=int, help="Number of seconds for the countdown timer")
parser_standalone.add_argument("max_errors", type=int, default=0, help="Maximum errors allowed")

parser_gui = subparsers.add_parser("gui", help="start server and wait for connection")


def linspace(start, stop, step):
	return list(i*step for i in range( int(start/step), int(stop/step) ) )

def make_beep_times(fulltime):
	result = ( linspace(0, 5, 0.2) + linspace(5, 10, 0.5) + linspace(10, 20, 1) + linspace(20, fulltime, 5) )[::-1]
	return result

def check_argument_validity(args):
	assert 10 <= args.difficulty <= 99
	assert args.time > 0
	assert args.max_errors >= 0

def check_existing_modules(bus):
	result = {}
	print("found the following modules (enumeration may take a while!)")
	print("---+-----------")
	print("   | revision  ")
	print("---+-----------")
	for m in "abcdefgh":#ijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789":
		description = bus.check_for_module(m)
		if description is not None:
			print(" {} | {}".format(m, description["revision"]))
			result[m] = description
	return result

class Gamemaster():
	def __init__(self, args):
		self.args = args

		self.bus = Bus.Bus(args.serial_device, BAUDRATE, debug=True)
		self.bus.drain()
	
		self.sound = SoundManager({"beep":"beep_short.wav", "beep_end": "beep_end.wav"})

		# check for control panel
		"""
		if not args.ignore_control_module:
			control_description = self.bus.check_for_module(Bus.CONTROL_MODULE)
			if control_description is None:
				raise Exception("no control module found!")
			self.bus.init_module(Bus.CONTROL_MODULE, True, "0000A", control_description["num_random"])
		"""

		# check other modules
		self.modules = check_existing_modules(self.bus)
		for m in args.disable:
			try:
				self.modules.pop(m)
			except KeyError:
				print("disable module {} which was not enumerated. typo?".format(m))

		if args.mode == "gui":
			self.server = Server("", self.modules)
	
	def get_game_info(self):
		if self.args.mode == "standalone":
			print("waiting 5s for game start...")
			time.sleep(5)
			return self.get_game_info_standalone()

		elif self.args.mode == "gui":
			# wait for "start" command
			while(True):
				if self.server._CheckForMessage():
					msg = self.server._PopMessage()
					if "start" in msg:
						d=msg["start"]
						return (d["seconds"], d["maxerrors"], d["serial"], d["modules"])
				else:
					print("waiting for start command...")
					time.sleep(0.5)
		else:
			raise NotImplementedError()

	def get_game_info_standalone(self):
		serial_number = str(self.args.difficulty) + str(random.randrange(0, 99)).zfill(2) + chr(0x41+random.randrange(0, 26))
		used_modules = random.sample(self.modules, self.args.num_modules)

		module_states = {m: {"enabled":m in used_modules, "random":[random.randrange(0,256) for i in range(self.modules[m]["num_random"])]} for m in self.modules}

		return (self.args.time, self.args.max_errors, serial_number, module_states)

	def should_abort(self):
		if self.args.mode == "gui":
			if self.server._CheckForMessage():
				msg = self.server._PopMessage()
				if "abort" in msg:
					return True
			return False
		else:
			return False

	def explode(self):
		print("BOOOM!")
		self.cleanup_after_game()

	def win(self):
		print("BOMB HAS BEEN DEFUSED!")
		self.cleanup_after_game()
	
	def cleanup_after_game(self):
		if self.args.mode == "standalone":
			print("game over, shutting down")
			sys.exit(0)

	def start_game(self):
		game_info = self.get_game_info()
		print(game_info)
		seconds, max_errors, serial_number, module_states = game_info
		# init all normal modules
		for m, state in module_states.iteritems():
			self.bus.init_module(m, state["enabled"], serial_number, state["random"])

		# wait for start switch on control panel
		"""
		if not args.ignore_control_module:
			bus.start_game(Bus.CONTROL_MODULE)
			while(True):
				continue_waiting, _ = bus.poll_status(Bus.CONTROL_MODULE)
				if not continue_waiting:
					break
		"""

		num_active_modules = sum(state["enabled"] for state in module_states.values())

		
		for m in module_states:
			self.bus.start_game(m)
		explosion_time = time.time() + seconds
		beeptimes = make_beep_times(seconds)
		next_beep_index = 0

		last_time_left = seconds
		last_num_lifes = max_errors

		while True:
			state = {"modules": {}}

			num_lifes = max_errors
			defused = 0
			for m in module_states:
				success, module_failures = self.bus.poll_status(m)
				state["modules"][m] = {"state": success, "failures": module_failures}
				if success in [0,1]:
					num_lifes -= module_failures
					if success:
						print("defused module. success = {}".format(success))
						defused += 1
				else:
					if self.args.mode == "standalone":
						raise Exception("state error in module {}: {} ({})".format(m, parse_errorcode_from_cpp("../../modules/libraries/BUMMSlave/BUMMSlave.cpp", success), module_failures))

			time_left = int(explosion_time - time.time())

			# SOUNDS
			# make countdown sounds
			if ( explosion_time - time.time() ) < self.sound["beep_end"].get_length():
				self.sound["beep_end"].play()
			elif ( explosion_time - time.time() ) < beeptimes[next_beep_index]:
				next_beep_index += 1
				self.sound["beep"].play()

			# BROADCAST STATE

			state["seconds"] = time_left
			state["lifes"] = num_lifes if num_lifes >= 0 else 0

			if last_time_left != time_left or last_num_lifes != num_lifes:
				print(time_left)
				self.bus.broadcast_status(time_left, num_lifes)
				last_time_left = time_left
				last_num_lifes = num_lifes

				if self.args.mode == "gui":
					self.server.send_game_update(state)

			# GAME END CONDITIONS
			# countdown over?
			if time_left <= 0:
				print("no time left")
				if self.args.mode == "gui":
					self.server.send_game_end(reason=1)
				self.bus.end_game(1)
				self.explode()
				break

			# too many failures?
			if num_lifes < 0:
				print("too many failures!")
				if self.args.mode == "gui":
					self.server.send_game_end(reason=2)
				self.bus.end_game(2)
				self.explode()
				break

			# defused?
			if defused == num_active_modules:
				if self.args.mode == "gui":
					self.server.send_game_end(reason=0)
				self.bus.end_game(0)
				self.win()
				break

			if self.should_abort():
				if self.args.mode == "gui":
					self.server.send_game_end(reason=3)
				self.bus.end_game(3)
				self.cleanup_after_game()
				break


def main():
	main_args = parser.parse_args()
	print(main_args.disable)
	gamemaster = Gamemaster(main_args)
	while(True):
		gamemaster.start_game()


if __name__=="__main__":
	main()

