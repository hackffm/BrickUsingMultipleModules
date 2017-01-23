import numpy as np
import random
from common import *

random.seed(0)

class Rule(object):
	def __eq__(self, other):
		return self.make_str() == other.make_str()

class DecisionRule(Rule):
	def __init__(self, condition, false_result, true_result):
		assert isinstance(condition, str)
		assert isinstance(false_result, Rule)
		assert isinstance(true_result, Rule)
		self.condition = condition
		self.false_result = false_result
		self.true_result = true_result

	def make_str(self):
		return "{}?({}):({})".format(self.condition, self.true_result.make_str(), self.false_result.make_str())

	def make_tex(self, all_rules):
		return r"\en{{If {0} is TRUE, obey rule {1}, else obey rule {2}}}\de{{Wenn {0} TRUE ist, befolge Regel {1}, ansonsten befolge Regel {2}}}\chde{{Wenn {0} wahr ist, folgen die Regeln {1}, {2}, sonst die Regeln}}".format(
				self.condition.upper(),
				get_number(all_rules, self.true_result),
				get_number(all_rules, self.false_result)
			)

class MultiRule(Rule):
	def __init__(self, subrules):
		assert isinstance(subrules, list)
		for r in subrules:
			assert isinstance(r, Rule)
		self.subrules = subrules

	def make_str(self):
		return "[{}]".format(",".join(r.make_str() for r in self.subrules))

	def make_tex(self, all_rules):
		return r"\en{{Obey the rules {0} and {1}}}\de{{Befolge Regel {0} und {1}}}\chde{{In Übereinstimmung mit den Regeln {0} und {1}}}".format(", ".join(str(get_number(all_rules, r)) for r in self.subrules[:-1]), get_number(all_rules, self.subrules[-1]))

class LeafRule(Rule):
	def __init__(self, switchresult):
		assert isinstance(switchresult, str)
		assert switchresult.upper() in output_names
		self.switchresult = switchresult

	def make_str(self):
		return self.switchresult

	def make_tex(self, all_rules):
		return r"\en{{Set {0} to {1}}}\de{{Schalte {0} auf {1}}}\chde{{Schalten {0} auf {1}}}".format(self.switchresult.upper(), "TRUE" if self.switchresult.isupper() else "FALSE")

def get_number(all_rules, rule):
	for i, r in enumerate(all_rules):
		if r == rule:
			return i+1
	raise Exception("rule {} not found!".format(rule.make_str()))
			

def add_rule_if_new(rules, rule):
	assert isinstance(rule, Rule)
	for r in rules:
		if r == rule:
			return r
	rules.append(rule)
	return rule

def make_leaf_rule(all_rules, tableline):
	switch_states = tableline[len(input_names):]
	return add_rule_if_new(all_rules, MultiRule(
		[
			add_rule_if_new(all_rules, LeafRule(name.upper() if switch_states[-i-1] else name.lower()))
			for i, name in enumerate(output_names)
		]))

def make_decision_rule(all_rules, condition, false_result, true_result):
	false_result = add_rule_if_new(all_rules, false_result)
	true_result = add_rule_if_new(all_rules, true_result)
	return add_rule_if_new(all_rules, DecisionRule(condition, false_result, true_result))

def make_recursive_rule(all_rules, table, depth):
	assert table.shape[0] == 2**(len(input_names)-depth)
	if table.shape[0] == 2:
		false_result = make_leaf_rule(all_rules, table[0])
		true_result = make_leaf_rule(all_rules, table[1])
		if false_result == true_result:
			return false_result
		return make_decision_rule(all_rules, input_names[0], false_result, true_result)
	else:
		false_result = make_recursive_rule(all_rules, table[:table.shape[0]//2], depth+1)
		true_result = make_recursive_rule(all_rules, table[table.shape[0]//2:], depth+1)
		if false_result == true_result:
			return false_result
		return make_decision_rule(all_rules, input_names[len(input_names)-1-depth], false_result, true_result)

def generate_text(all_rules):
	result = ""
	for i, rule in enumerate(all_rules):
		result += r"\item[\en{{Rule}}\de{{Regel}}\chde{{Regel}} {0}]: ".format(i+1) + rule.make_tex(all_rules) + "\n"
	return result

def main():
	tables = np.load(TABLE_FILE)
	text = ""
	root_rule_table = ""

	for level, table in enumerate(tables):
		rules = []
		root_rule = make_recursive_rule(rules, table, 0)
		random.shuffle(rules)
		root_rule_number = get_number(rules, root_rule)

		if configs[level]["show_root_rule"]:
			root_rule_table += "{} & {} \\\\\n".format(configs[level]["title"], root_rule_number)

		text += "\n"+r"\section*{{\en{{Series {0}}}\de{{Serien {0}}}\chde{{Serien {0}}}}}".format(configs[level]["title"])+"\n\n"
		text += r"\begin{description}"+"\n"
		ruletext = generate_text(rules)
		if configs[level]["shuffle_rules_again"]:
			textlist = ruletext.split("\n")
			random.shuffle(textlist)
			ruletext = "\n".join(textlist)
		text += ruletext
		text += r"\end{description}"+"\n"

	with open("flowchoice_autogen.tex", "w") as f:
		f.write(r"\begin{table}\begin{center}\begin{tabular}{|l|l|}\hline"+"\n")
		f.write(r"\en{Series}\de{Seriennummer}\chde{Serien} & \en{rule}\de{Regel}\chde{Regel}\\\hline"+"\n")
		f.write(root_rule_table)
		f.write(r"\hline\end{tabular}\caption{\en{Most important Rules}\de{Wichtigste Regeln}\chde{Die Hauptregel}}\label{tab:root_rules}\end{center}\end{table}"+"\n")
		f.write(text)

main()
