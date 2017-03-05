import tkinter as tk
from tkinter import ttk, messagebox
import time
import random
import subprocess
import sys

sys.path.append("../gamemaster")
from parse_errorcode_from_cpp import parse_errorcode_from_cpp

COL_ID = 0
COL_REVISION = 1
COL_NEXTSTATE = 2
COL_RANDOMNUMBER = 3
COL_STATE = 4
COL_FAILURES = 5
COL_DESCRIPTION = 6
COL_SOLVE = 7

"""
center area (table)
	module id
	module revision (assumed from config and real, if different)
	module state (inactive, armed, disarmed, error)
	next state (on, off, random)
	failure counter
	description from module_solver
	button for more info (hints and solution)
"""

WIDTH_SHORT = 10
table_default_style = dict(width=WIDTH_SHORT, relief=tk.RIDGE, anchor=tk.CENTER)
current_display_default_style = dict(font="monospace 80", justify=tk.RIGHT, width=5)
next_info_default_entry_style = dict( width=5, justify=tk.LEFT )

class Application(ttk.Frame):
	def __init__(self, connection, expected_revisions, master=None):
		ttk.Frame.__init__(self, master)

		self.lifes_at_start = 0

		self.connection = connection
		self.disable_while_running = []
		self.is_running = False

		self.grid(sticky=tk.N+tk.S+tk.E+tk.W)
		self.module_controls = {}
		self.createWidgets()


		print("waiting for message")
		while not connection._CheckForMessage():
			time.sleep(0.01)

		print("message found")
		hardware_description = connection._PopMessage()["capabilities"]

		self.module_descriptions = hardware_description["modules"]

		self.num_modules.set(len(self.module_descriptions))

		for i, module_id in enumerate(sorted(self.module_descriptions.keys())):
			self.add_module_line(i+1, module_id, self.module_descriptions[module_id], expected_revisions)

		self.randomize()

		self.poll_network()

	def createWidgets(self):
		self.grid_columnconfigure(0, weight=1)

		# **************
		# current display
		# **************
		self.current_display = ttk.Frame(self)
		self.current_display.grid(column=0, row=1)

		# current countdown
		self.current_countdown = tk.StringVar()
		current_countdown = tk.Label(self.current_display, textvariable=self.current_countdown, foreground="red", **current_display_default_style)
		current_countdown.grid(row=0, column=1, sticky=tk.N+tk.S+tk.E+tk.W)

		# current lifes
		self.current_lifes = tk.StringVar(self.lifes_at_start)
		current_lifes = tk.Label(self.current_display, textvariable=self.current_lifes, foreground="green" , **current_display_default_style)
		current_lifes.grid(row=0, column=4, sticky=tk.N+tk.S+tk.E+tk.W)

		# start button
		self.btn_start = ttk.Button(self.current_display)
		self.btn_start["text"] = "Start"
		self.btn_start["command"] = self.start_new_game
		self.btn_start["state"] = tk.DISABLED
		self.btn_start.grid(row=1, column=2)

		# abort button
		self.btn_abort = ttk.Button(self.current_display)
		self.btn_abort["text"] = "Abort"
		self.btn_abort["command"] = self.abort_game
		self.btn_abort.grid(row=1, column=3)

		# error display
		self.error_display = ttk.Label(self.current_display, text="", justify=tk.CENTER, foreground="red")
		self.error_display.grid(row=2, column=1, columnspan=4)


		# **************
		# next game info
		# **************
		self.next_game_info = ttk.Frame(self)
		self.next_game_info.grid(column=0, row=2)

		# fill space on sides
		self.next_game_info.grid_columnconfigure(0, weight=1)
		ttk.Frame(self.next_game_info).grid(row=0, column=0)
		self.next_game_info.grid_columnconfigure(3, weight=1)
		ttk.Frame(self.next_game_info).grid(row=0, column=3)

		# seconds
		ttk.Label(self.next_game_info, text="seconds", justify=tk.RIGHT).grid(row=1, column=1)
		self.seconds = tk.StringVar(value="300")
		seconds = tk.Entry(self.next_game_info, textvariable=self.seconds, **next_info_default_entry_style)
		seconds.grid(row=1, column=2, sticky=tk.N+tk.S+tk.W)
		self.make_red_on_invalid_change(self.seconds, seconds, self.parse_seconds)
		self.seconds.trace("w", lambda *args: self.disable_widgets_if_necessary())

		# maxerrors
		ttk.Label(self.next_game_info, text="max errors allowed", justify=tk.RIGHT).grid(row=2, column=1)
		self.maxerrors = tk.StringVar(value="0")
		maxerrors = tk.Entry(self.next_game_info, textvariable=self.maxerrors, **next_info_default_entry_style)
		maxerrors.grid(row=2, column=2, sticky=tk.N+tk.S+tk.W)
		self.make_red_on_invalid_change(self.maxerrors, maxerrors, self.parse_maxerrors)
		self.maxerrors.trace("w", lambda *args: self.disable_widgets_if_necessary())



		# serial
		ttk.Label(self.next_game_info, text="serial number", justify=tk.RIGHT).grid(row=3, column=1)
		self.serial = tk.StringVar()
		serial = tk.Entry(self.next_game_info, textvariable=self.serial, **next_info_default_entry_style)
		serial.grid(row=3, column=2
				, sticky=tk.N+tk.S+tk.W
				)
		self.make_red_on_invalid_change(self.serial, serial, self.parse_serial)
		self.serial.trace("w", lambda *args: self.disable_widgets_if_necessary())
		self.disable_while_running.append(serial)

		# number of modules
		ttk.Label(self.next_game_info, text="number of modules", justify=tk.RIGHT).grid(row=4, column=1)
		self.num_modules = tk.StringVar(value="1")
		num_modules = tk.Entry(self.next_game_info, textvariable=self.num_modules, **next_info_default_entry_style)
		num_modules.grid(row=4, column=2
				, sticky=tk.N+tk.S+tk.W
				)
		self.make_red_on_invalid_change(self.num_modules, num_modules, self.parse_num_modules)
		self.num_modules.trace("w", lambda *args: self.disable_widgets_if_necessary())
		self.disable_while_running.append(num_modules)


		# randomize button
		self.btn_randomize = ttk.Button(self.next_game_info, text="randomize", command=self.randomize)
		self.btn_randomize.grid(row=5, column=1, columnspan=2)
		self.disable_while_running.append(self.btn_randomize)




		# table
		self.table = ttk.Frame(self)
		self.table.grid(column=0, row=3, sticky=tk.N+tk.S+tk.E+tk.W)
		self.table.grid_columnconfigure(COL_DESCRIPTION, weight=1)

		ttk.Label(self.table, text="ID", **table_default_style).grid(row=0, column=COL_ID, sticky=tk.N+tk.S+tk.E+tk.W)
		ttk.Label(self.table, text="REV", **table_default_style).grid(row=0, column=COL_REVISION, sticky=tk.N+tk.S+tk.E+tk.W)
		ttk.Label(self.table, text="NEXT", **table_default_style).grid(row=0, column=COL_NEXTSTATE, sticky=tk.N+tk.S+tk.E+tk.W)
		ttk.Label(self.table, text="RANDOM", **table_default_style).grid(row=0, column=COL_RANDOMNUMBER, sticky=tk.N+tk.S+tk.E+tk.W)
		ttk.Label(self.table, text="STATE", **table_default_style).grid(row=0, column=COL_STATE, sticky=tk.N+tk.S+tk.E+tk.W)
		ttk.Label(self.table, text="FAIL", **table_default_style).grid(row=0, column=COL_FAILURES, sticky=tk.N+tk.S+tk.E+tk.W)
		ttk.Label(self.table, text="DESCRIPTION", **table_default_style).grid(row=0, column=COL_DESCRIPTION, sticky=tk.N+tk.S+tk.E+tk.W)
		#ttk.Label(self.table, text="", **table_default_style).grid(row=0, column=COL_SOLVE)

	def add_module_line(self, row, module_id, module_desc, expected_revisions):
		self.module_controls[module_id] = {}
		controls = self.module_controls[module_id]
		module_id_widget = ttk.Label(self.table, text=module_id, **table_default_style)
		module_id_widget.grid(row=row, column=COL_ID, sticky=tk.N+tk.S+tk.E+tk.W)

		# revision
		revision = module_desc["revision"]
		if expected_revisions is None:
			rev_text = "{}*".format(revision)
			color = None
		else:
			try:
				if revision == int(expected_revisions[module_id]):
					rev_text = revision
					color = None
				else:
					rev_text = "{} / {}".format(revision, expected_revisions[module_id])
					color = "red"
			except KeyError:
				rev_text = "{} / ?".format(revision)
				color = "red"

		module_revision = ttk.Label(self.table, text=rev_text, background=color, **table_default_style)
		module_revision.grid(row=row, column=COL_REVISION, sticky=tk.N+tk.S+tk.E+tk.W)

		# nextstate
		module_nextstate = ttk.Combobox(self.table, values=["on", "random", "off"], state="readonly")
		module_nextstate.grid(row=row, column=COL_NEXTSTATE, sticky=tk.N+tk.S+tk.E+tk.W)
		module_nextstate.current(1)
		controls["nextstate"] = module_nextstate

		# random value
		random_value = tk.StringVar()
		module_random = tk.Entry(self.table, textvariable=random_value, disabledforeground="black")
		module_random.grid(row=row, column=COL_RANDOMNUMBER, sticky=tk.N+tk.S+tk.E+tk.W)
		controls["random"] = module_random
		controls["random_value"] = random_value
		self.make_red_on_invalid_change(random_value, module_random, lambda module_id=module_id: self.parse_randomness_string(module_id))
		random_value.trace("w", lambda *args: self.disable_widgets_if_necessary())
		self.disable_while_running.append(module_random)

		# state
		module_state = ttk.Label(self.table, text="?", **table_default_style)
		module_state.grid(row=row, column=COL_STATE, sticky=tk.N+tk.S+tk.E+tk.W)
		controls["state"] = module_state

		# failure counter
		module_fail = ttk.Label(self.table, text="?", **table_default_style)
		module_fail.grid(row=row, column=COL_FAILURES, sticky=tk.N+tk.S+tk.E+tk.W)
		controls["fail"] = module_fail

		# ui description
		module_description = ttk.Label(self.table, text="?", relief=tk.RIDGE)
		module_description.grid(row=row, column=COL_DESCRIPTION, sticky=tk.N+tk.S+tk.E+tk.W)
		controls["desc"] = module_description

		# solve button
		module_solve = ttk.Button(self.table, text="solve", command=lambda module_id=module_id: self.solve(module_id), width=WIDTH_SHORT)
		module_solve.grid(row=row, column=COL_SOLVE)
	
	def make_red_on_invalid_change(self, variable, widget, callback):
		def red_if_invalid(widget, validator_callback):
			try:
				validator_callback()
			except ValueError as e:
				widget["background"] = "red"
			else:
				widget["background"] = "white"
		variable.trace("w", lambda *args, widget=widget, callback=callback: red_if_invalid(widget, callback))

	
	def parse_seconds(self):
		result = int(self.seconds.get())
		if result <= 20:
			raise ValueError("seconds has to be >20")
		return result
	
	def parse_maxerrors(self):
		result = int(self.maxerrors.get())
		if result < 0:
			raise ValueError("maxerrors has to be >=0")
		return result

	def parse_num_modules(self):
		result = int(self.num_modules.get())
		if result <= 0:
			raise ValueError("num_modules has to be >0")

		forced_modules, random_modules = self.get_forced_and_random_modules()
		if not len(forced_modules) <= result <= len(forced_modules)+len(random_modules):
			raise ValueError("num_modules has to be in [{}, {}]".format(len(forced_modules), len(forced_modules)+len(random_modules)))

		return result
	
	def parse_serial(self):
		if len(self.serial.get()) != 5:
			raise ValueError("serial number must have 5 digits")
		if not 1000 <= int(self.serial.get()[0:4]) <= 9999:
			raise ValueError("numeric part of serial number invalid")
		if not "A" <= self.serial.get()[4] <= "Z":
			raise ValueError("alpha part of serial number invalid")
		return self.serial.get()

	def parse_randomness_string(self, module_id):
		string = self.module_controls[module_id]["random_value"].get()
		integers = [int(x) for x in string.split()]
		for i in integers:
			if not 0 <= i < 256:
				raise ValueError("all numbers in string should be uint8_t integers")
		if len(integers) != self.module_descriptions[module_id]["num_random"]:
			raise ValueError("module {} requires {} random numbers ({} given)".format(module_id, self.module_descriptions[module_id]["num_random"], len(integers)))
		return integers

	def check_all_validities(self):
		try:
			self.gather_new_game_dict()

		except ValueError:
			return False
		else:
			return True
	
	def disable_widgets_if_necessary(self):
		for widget in self.disable_while_running:
			widget["state"] = tk.DISABLED if self.is_running else tk.NORMAL

		try:
			self.gather_new_game_dict()
			valid = True
			self.error_display["text"] = ""
		except Exception as e:
			valid = False
			self.error_display["text"] = str(e)

		self.btn_start["state"] = tk.DISABLED if self.is_running or not valid else tk.NORMAL
		#self.btn_abort["state"] = tk.NORMAL if self.is_running else tk.DISABLED


	def poll_network(self):
		if self.connection._CheckForMessage():
			msg = self.connection._PopMessage()

			if "state" in msg:
				self.handle_update_modules(msg["state"])
			elif "end" in msg:
				self.handle_game_end(msg["end"])
			else:
				print("unknown message: {}".format(msg))

		self.after(10, self.poll_network)

	def handle_update_modules(self, d):
		self.is_running = True
		for module_id, module_state in d["modules"].items():
			self.update_module(module_id, module_state)
		self.current_countdown.set(d["seconds"])
		self.current_lifes.set(d["lifes"])
		self.disable_widgets_if_necessary()
	
	def handle_game_end(self, d):
		self.is_running = False
		self.disable_widgets_if_necessary()
		# TODO: add to highscore/statistics

	def update_module(self, module_id, module_state):
		controls = self.module_controls[module_id]

		has_error = False

		if module_state["state"] == 0: # armed
			controls["state"]["background"] = "red"
			controls["state"]["text"] = "ARMED"
		elif module_state["state"] == 1: # defused
			controls["state"]["background"] = "green"
			controls["state"]["text"] = "DEFUSED"
		else:
			controls["state"]["background"] = "orange"
			controls["state"]["text"] = "ERROR"
			controls["desc"]["text"] = parse_errorcode_from_cpp("../../modules/libraries/BUMMSlave/BUMMSlave.cpp", module_state["state"])
			has_error = True

		if not has_error:
			controls["fail"]["text"] = module_state["failures"]

	def solve(self, module_id):
		try:
			text = self.get_solver_info(module_id, "hints") + "\n\n" + self.get_solver_info(module_id, "solution")
		except:
			text = "NOT AVAILABLE"
		messagebox.showinfo("hints and solution for module {}".format(module_id), text)
	
	def get_forced_and_random_modules(self):
		used_modules = [module_id for module_id, controls in self.module_controls.items() if controls["nextstate"].current() == 0]
		random_modules = [module_id for module_id, controls in self.module_controls.items() if controls["nextstate"].current() == 1]
		return used_modules, random_modules

	def gather_new_game_dict(self):
		num_modules = self.parse_num_modules()
		forced_modules, random_modules = self.get_forced_and_random_modules()

		used_modules = forced_modules + random.sample(random_modules, num_modules-len(forced_modules))

		result = {
				"seconds": self.parse_seconds(),
				"maxerrors": self.parse_maxerrors(),
				"serial": self.parse_serial(),
				"modules":
				{
					module_id: {
						"enabled": module_id in used_modules,
						"random": self.parse_randomness_string(module_id)
					}
					for module_id in self.module_descriptions
				}
			}

		return result


	def start_new_game(self):
		game_dict = self.gather_new_game_dict()
		print(game_dict)
		self.connection.send_start(game_dict)
		self.is_running = True

		# describe-display
		for module_id in self.module_descriptions:
			try:
				ui_description = self.get_solver_info(module_id, "describe")
			except:
				ui_description = "NOT AVAILABLE"
			self.module_controls[module_id]["desc"]["text"] = ui_description

		self.disable_widgets_if_necessary()

	def abort_game(self):
		self.connection.send_abort()

		self.is_running = False
		self.disable_widgets_if_necessary()
	
	def randomize(self):
		try:
			difficulty = int(self.serial.get()[0:2])
			if difficulty < 10:
				raise Exception()
		except:
			difficulty = random.randint(10, 99)
		new_serial = str(difficulty) + str(random.randrange(0, 99)).zfill(2) + chr(0x41+random.randrange(0,26))
		self.serial.set(new_serial)

		for module_id, controls in self.module_controls.items():
			num_random = self.module_descriptions[module_id]["num_random"]
			controls["random_value"].set(" ".join(str(random.randrange(0, 256)) for i in range(num_random)))
	
	def get_solver_info(self, module_id, mode):
		cwd = "../../modules/{}/".format(module_id)
		return (subprocess.run([cwd+"module_solver.py", mode, self.serial.get()] + [str(i) for i in self.parse_randomness_string(module_id)], cwd=cwd, stdout=subprocess.PIPE).stdout[:-1]).decode("utf-8")

