#!/usr/bin/python3
import sys
import argparse
import tkinter as tk
from master_gui_main_window import Application

sys.path.append("../lib")
from client import Client

parser = argparse.ArgumentParser(description="BUMM master gui")
parser.add_argument("hostname", type=str, help="hostname of gamemaster")
parser.add_argument("--expected-revisions", type=argparse.FileType("r"), nargs="?", default=None, help="filename of module_id=revision pairs of expected revisions (this file should match the printed out manual)")
args = parser.parse_args()

connection = Client(args.hostname)

if args.expected_revisions is None:
	expected_revisions = None
else:
	expected_revisions = {line.split("=")[0]: line.split("=")[1] for line in args.expected_revisions}

root = tk.Tk()
root.wm_title("BUMM Master control UI")
root.grid_columnconfigure(0, weight=1)
app = Application(connection, master=root, expected_revisions=expected_revisions)
app.mainloop()
