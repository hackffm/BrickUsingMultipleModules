from common import *

# generate manual figures
with open("manual_figures_autogen.tex", "w") as f:
	invert_switches_table = ""
	for row in range(len(switch_inverts)//5):
		for col in range(5):
			i = col+row*5
			invert_switches_table += "xx{}x".format(switch_inverts[i])
			if col < 4:
				invert_switches_table += " &"
			else:
				invert_switches_table += " \\\\"

	f.write(r"""
	\begin{{table}}[b]
		\begin{{center}}
			\begin{{tabular}}{{ccccc}}
			{}
			\end{{tabular}}
		\end{{center}}
		\caption{{
		\en{{List of serial numbers with inverted switch directions (down=FALSE)}}
		\de{{Liste der Seriennummern mit invertierten Schaltern (unten=FALSE)}}
		}}
		\label{{tab:b_switch_inversion}}
	\end{{table}}
	""".format( invert_switches_table ))

	f.write(r"\newcommand{{\ledInversionNumbers}}{{{}}}".format(", ".join("xxxx"+l for l in led_inverts[:-1]) + " or xxxx" + led_inverts[-1]))

	for i, config in enumerate(configs):
		f.write(r"""
		\begin{{figure}}
			\begin{{center}}
			\includegraphics[scale=0.4]{{wires_autogen_{i}}}
			\caption{{
			\en{{Internal wiring for series {title}}}
			\de{{Interne Verdrahtung der Serie {title}}}
			}}
			\end{{center}}
		\end{{figure}}""".format(i=i, title=config["title"]))


