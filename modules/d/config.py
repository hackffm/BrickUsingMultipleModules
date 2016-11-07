"""
definitions:
	0: green (false)
	1: red (true)
"""

parameters = [
	{
		"random_seed": 0,
		"difficulty_interval": (10, 20),
		"blink_speed": 1000, # milliseconds
		"num_blinks": 3,
		"num_rounds": 2,
		"show_ordered_in_manual": True,
		"button_modes": "GR"
	},
	{
		"random_seed": 0,
		"difficulty_interval": (20, 30),
		"blink_speed": 1000, # milliseconds
		"num_blinks": 5,
		"num_rounds": 2,
		"show_ordered_in_manual": True,
		"button_modes": "GREV"
	},
	{
		"random_seed": 0,
		"difficulty_interval": (30, 50),
		"blink_speed": 500, # milliseconds
		"num_blinks": 6,
		"num_rounds": 3,
		"show_ordered_in_manual": True,
		"button_modes": "GREV"
	},
	{
		"random_seed": 0,
		"difficulty_interval": (50, 80),
		"blink_speed": 500, # milliseconds
		"num_blinks": 7,
		"num_rounds": 5,
		"show_ordered_in_manual": True,
		"button_modes": "GREV"
	},
	{
		"random_seed": 0,
		"difficulty_interval": (80, 100),
		"blink_speed": 300, # milliseconds
		"num_blinks": 8,
		"num_rounds": 5,
		"show_ordered_in_manual": False,
		"button_modes": "GREV"
	}
]

V_mode_letters = "AEIOU"

button_modes = {
	"G": {
		"description": "\en{press the green button}\de{den grünen Knopf drücken}",
		"solver": "False",
		"code": "false"
	},
	"R": {
		"description": "\en{press the red button}\de{den roten Knopf drückem}",
		"solver": "True",
		"code": "true"
	},
	"E": {
		"description": "\en{if the module modifier number is even, press the red button, else press the green button}\de{wenn die Modulseriennummer gerade ist, den roten Knopf drücken, sonst den grünen}",
		"solver": "(int(serial[3]) % 2 == 0)",
		"code": """ !((bs.serialNumber[3]-'0') & 1) """
	},
	"V": {
		"description": "\en{{if the serial number ends with a {0}, press the red button, else press the green button}}\de{{wenn die Seriennummer mit {0} endet, den roten Knopf drücken, sonst den grünen}}".format(", ".join(V_mode_letters[:-1]) + " or " + V_mode_letters[-1]),
		"solver": "serial[4] in ['{}']".format("','".join(V_mode_letters)),
		"code": " ( " + " || ".join(" (bs.serialNumber[4] == '{}') ".format(letter) for letter in V_mode_letters) + " ) "
	}
#	,"O": {
#		"description": "if this is the first, third, fifth, ... command, press the red button, else press the green button",
#		"solver": "command_number % 2 == 0", # (we start with 0, normal people with 1)
#		"code": 
#	}
}
