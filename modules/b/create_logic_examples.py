import pygraphviz as pgv

node_kwargs = {"fontname":"Courier"}
params = {
	False : dict(color="red", fontname="Courier", style="dashed"),
	True : dict(color="green", fontname="Courier")
}
print(params[True])

def main():
	for gate_name, gate_f in (
			("nor", lambda a, b: not (a or b)),
			("nand", lambda a, b: not (a and b))
			):
		for in1, in2 in ((False, False), (False, True), (True, True)):
			result = gate_f(in1, in2)
			g = pgv.AGraph(directed=True)

			g.add_node("in1", label=str(in1).upper(), **params[in1])
			g.add_node("in2", label=str(in2).upper(), **params[in2])
			g.add_node("gate", label="{}\n{}".format(gate_name, str(result).upper()), **params[result])
			g.add_node("result", style="invis")

			g.add_edge("in1", "gate", **params[in1])
			g.add_edge("in2", "gate", **params[in2])
			g.add_edge("gate", "result", **params[result])

			g.layout(prog='dot')
			g.draw("logic_example_autogen_{}_{}_{}.pdf".format(gate_name, in1, in2))

main()
