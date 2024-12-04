conda activate gen_analysis

# create a css file
# pygmentize -S default -f html -a .codehilite > not_correct_codehilite.css

# need to either replace or add something like this to the css file
# h1 { color: #1E90FF; } /* DodgerBlue */
# h2 { color: #32CD32; } /* LimeGreen */
# h2.mouse-phenotype { color: #FFA500; } /* Orange */



python convert_md_html_pdf.py /home/delpropo/github/gen_analysis/data/processed/20241119T0832_test_file_1.tsv_output.md 

# This doesn't work.
# pandoc example.html -o example.pdf --css codehilite.css
