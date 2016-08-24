#!/usr/bin/python3
import random
import pickle
import config

result = []
for p in config.parameters:
	random.seed(p["random_seed"])
	count = 2 ** p["num_blinks"]
	result.append([random.choice(p["button_modes"]) for i in range(count)])

with open("lookuptable_autogen.dat", "wb") as f:
	pickle.dump(result, f)
