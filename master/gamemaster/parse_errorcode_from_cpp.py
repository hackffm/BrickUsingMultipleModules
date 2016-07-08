import re

regex = re.compile(r"^#define ERROR_(\w+) (\w+)$")

def parse_errorcode_from_cpp(filename, code):
	result = None
	with open(filename, "r") as f:
		for line in f:
			match = regex.match(line)
			if match:
				if int(match.group(2), 0) == code:
					if result is None:
						result = match.group(1)
					else:
						raise Exception("ambiguous errorcode ({}) could be either {} or {}".format(code, result, match.group(1)))
	return "UNKNOWN ERROR CODE ({})".format(code) if result is None else result
