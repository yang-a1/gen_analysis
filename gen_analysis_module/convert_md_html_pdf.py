import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
import argparse
import weasyprint
from gen_analysis_module.config import CSS_CONTENT, PROMPTS_JSON_PATH
import os
import json


def html_class_assignment(prompts_json_path, CSS_CONTENT, full_html_content):

    with open(prompts_json_path, 'r') as file:
        prompts = json.load(file)

    # create a key value pair where the key is the prompt and the value is <h2 class="omim_prompt">
    html_update_dicitonary = {key: f'<h2 class="{key}">' for key in prompts.keys()}

    # open the full_html_content and replace all lines that have <h2> {key} </h2> with  <h2 class="{key}"> {key} </h2>
    for key, value in html_update_dicitonary.items():
        full_html_content = full_html_content.replace(f'<h2>*{key}*</h2>', value)

    return full_html_content






def markdown_to_html(markdown_file, CSS_CONTENT, prompts_json_path):
    """
    Converts a Markdown file to an HTML string with optional CSS styling.
    Args:
        markdown_file (str): The full path to the Markdown file to be converted.
        CSS_CONTENT (str): A string containing CSS styles to be applied to the HTML content.  This applies the color scheme to the code blocks.
    Returns:
        str: The converted HTML content as a string, including the provided CSS styles.
    Example:
        html_content = markdown_to_html('example.md', 'body { font-family: Arial; }')
    """

    # Read the Markdown file
    with open(markdown_file, 'r') as md_file:
        md_content = md_file.read()

    extensions = [
        CodeHiliteExtension(linenums=False, guess_lang=False)
    ]
    md = markdown.Markdown(extensions=extensions)
    html_content = md.convert(md_content)

    full_html_content = f'''
    <html>
    <head>
        <style>
        {CSS_CONTENT}
        </style>
    </head>
    <body>
    {html_content}
    </body>
    </html>
    '''

    return html_class_assignment(prompts_json_path, CSS_CONTENT, full_html_content)






def save_html(full_html_content, output_file_html):
    with open(output_file_html, 'w') as html_file:
        html_file.write(full_html_content)


def save_pdf(full_html_content, output_file_pdf):
    weasyprint.HTML(string=full_html_content).write_pdf(output_file_pdf)


def complete_html_pdf(markdown_file, CSS_CONTENT, prompts_json_path):
    """
    Combines all functions to convert markdown to html and pdf and save the files.
    Args:
        markdown_file (str): The full path to the Markdown file to be converted.
        CSS_CONTENT (str): A string containing CSS styles to be applied to the HTML content.  This applies the color scheme to the code blocks.
    Returns:
        bool: True if successful, False otherwise.
    Example:
        complete_html_pdf('example.md', 'gen_analysis.css')
    """
    try:
        if not markdown_file.endswith('.md'):
            raise ValueError("The input file must have a '.md' extension")
        else:
            base_filename = markdown_file[:-3]
            # Add the '.html' extension to the file name
            output_file_html = base_filename + '.html'
            # add the '.pdf' extension to the file name
            output_file_pdf = base_filename + '.pdf'

        # Convert Markdown to HTML with Syntax Highlighting
        full_html_content = markdown_to_html(markdown_file, CSS_CONTENT, prompts_json_path)

        save_html(full_html_content, output_file_html)
        save_pdf(full_html_content, output_file_pdf)

        return True
    except Exception as e:
        print(f"An error occurred: {e}")
        return False















if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert Markdown to HTML with syntax highlighting.')
    parser.add_argument('input_file', help='The Markdown file to convert.')


    args = parser.parse_args()
    markdown_file = args.input_file

    # confirm that the input file is a markdown file path exists
    if not os.path.exists(markdown_file):
        raise FileNotFoundError(f"The file '{markdown_file}' does not exist.")

    print(CSS_CONTENT)



    if complete_html_pdf(markdown_file, CSS_CONTENT, PROMPTS_JSON_PATH):
        print("HTML and PDF files generated successfully with syntax highlighting.")
    else:
        print("An error occurred during file conversion.")

    # prompts = prompts_color_assignment(PROMPTS_JSON_PATH, CSS_CONTENT)

    # print(prompts)