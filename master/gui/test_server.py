#!/usr/bin/python3
import time
import sys
import random

sys.path.append("../lib")
from server import Server

if __name__ == "__main__":
	server = Server("",{
		"a": {"revision": 3, "num_random": 0},
		"b": {"revision": 1, "num_random": 1},
		"c": {"revision": 2, "num_random": 1}
	})
	state = {"seconds":49, "modules":
		{
			"a": {"state": 0, "failures": 0},
			"b": {"state": 0, "failures": 0},
			"c": {"state": 2, "failures": 0}
		}}

	running = False

	while(True):
		if server._CheckForMessage():
			msg = server._PopMessage()
			if "start" in msg:
				running = True
				state["seconds"] = msg["start"]["seconds"]
			elif "abort" in msg:
				running = False
				server.send_game_end(reason=3)
			else:
				print(msg)
		time.sleep(1.0)

		state["seconds"] -= 1
		if random.randrange(20) == 0:
			state["modules"]["b"]["state"] = 1

		if running:
			server.send_game_update(state)

		if state["seconds"] <= 0:
			server.send_game_end(reason=1)
			running = False

