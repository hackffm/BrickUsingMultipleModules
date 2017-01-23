.PHONY: manual

manual: manual_en.pdf manual_de.pdf manual_chde.pdf

manual_%.pdf: manual.tex
	pdflatex -jobname manual_$* "\input{../$*.tex}\input{manual.tex}"
	pdflatex -jobname manual_$* "\input{../$*.tex}\input{manual.tex}"

