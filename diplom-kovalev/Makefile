all:
	dot images/general-arch.dot -Tpdf > images/general-arch.pdf
	dot images/server-threads.dot -Tpdf > images/server-threads.pdf
	dot images/server-collect-dataflow.dot -Tpdf > images/server-collect-dataflow.pdf
	inkscape -f images/general-arch-pict.svg -A images/general-arch-pict.pdf
	inkscape -f images/general-arch-pict.svg -e images/general-arch-pict.png
	dot images/server-perform-dataflow.dot -Tpdf > images/server-perform-dataflow.pdf
	pdflatex diplom-kovalev.tex
	bibtex diplom-kovalev
	pdflatex diplom-kovalev.tex
	bibtex diplom-kovalev
	pdflatex diplom-kovalev.tex
	pdflatex presentation-kovalev.tex
	pdflatex presentation-kovalev.tex
	pdflatex presentation-kovalev-raster.tex
	pdflatex presentation-kovalev-raster.tex
clean:
	rm -rf *.aux *.log *.toc *.out *.blg *.bbl
