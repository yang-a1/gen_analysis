import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
import argparse
import weasyprint

parser = argparse.ArgumentParser(description='Convert Markdown to HTML with syntax highlighting.')
parser.add_argument('input_file', help='The Markdown file to convert.')
parser.add_argument('-o', '--output_file', default='output.html', help='The output HTML file.')

args = parser.parse_args()
markdown_file = args.input_file
output_file = args.output_file




def markdown_to_html(md_content):
    extensions = [
        CodeHiliteExtension(linenums=False, guess_lang=False)
    ]
    md = markdown.Markdown(extensions=extensions)
    html = md.convert(md_content)
    return html

# Read the Markdown file
with open(markdown_file, 'r') as md_file:
    md_content = md_file.read()

# Convert Markdown to HTML with Syntax Highlighting
html_content = markdown_to_html(md_content)

# Read the CSS file
with open('codehilite.css', 'r') as css_file:
    css_content = css_file.read()

# Compose the final HTML with the CSS
full_html_content = f'''
<html>
<head>
    <style>
    {css_content}
    </style>
</head>
<body>
{html_content}
</body>
</html>
'''

# Save the HTML to a file
with open(output_file, 'w') as html_file:
    html_file.write(full_html_content)

print("HTML file generated successfully with syntax highlighting: example.html")




# Read the HTML file
with open(output_file, 'r') as html_file:
    html_content = html_file.read()

# replace html at the end of output_file with pdf
output_file_pdf = output_file.replace('.html', '.pdf')

# Convert HTML to PDF
weasyprint.HTML(string=html_content).write_pdf(output_file_pdf)