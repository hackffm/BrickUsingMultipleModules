#!/usr/bin/python3
import sys
import random

random.seed(sys.argv[1])

num_stages = 3

print("generating table...")
table = []
for stage in range(num_stages):
	subtable = []
	for led_input in range(256):
		subtable.append(random.randrange(16))
	table.append(subtable)

print("generating code")
codes = []
for stage in range(num_stages):
	codes.append(",\n".join([("\t\t" + ", ".join((str(x) for x in table[stage][i*16:(i+1)*16]))) for i in range(16)]))

code = "uint8_t lookup[] = {\n"
code += "\n\t},{\n".join(codes)
code += "\n};\n"

with open("lookuptable.cpp","w") as f:
	f.write(code)

html_template = """
<html>
<body>
<table border=\"1\">
{}
</table>
</body>
</html>
"""

header1 = "<tr><td></td><td></td>" + "".join(("<td colspan=\"4\">{}</td>".format(i) for i in range(4))) + "</tr>\n"
header2 = "<tr><td></td><td></td>" + "".join(("<td>{}</td>".format(i) for j in range(4) for i in range(4))) + "</tr>\n"

content = ""
for i3 in range(4):
	for i2 in range(4):
		content += "<tr><td>{}</td><td>{}</td>".format(i3,i2)
		for i1 in range(4):
			for i0 in range(4):
				cell = "/".join((hex(table[stage][i0+4*i1+16*i2+64*i3])[-1] for stage in range(num_stages)))
				content += "<td>{}</td>".format(cell)
		content += "</tr>\n"

html = html_template.format( header1 + header2 + content)

with open("manual.html","w") as f:
	f.write(html)
