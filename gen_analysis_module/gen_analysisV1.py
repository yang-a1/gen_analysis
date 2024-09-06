import csv
import os
from collections import defaultdict
import openai  
from dotenv import load_dotenv, find_dotenv 
from docx import Document

# Load the .env file and get the OpenAI API Key from the .env file
# The .env file should contain the line: OPENAI_API_KEY=your_openai_api_key
_ = load_dotenv(find_dotenv())
openai.api_key = os.environ.get('OPENAI_API_KEY')

# Function to generate notes using ChatGPT
def generate_note(prompt):
    """
    Generates a note using OpenAI's GPT model based on the provided prompt.

    Parameters:
    prompt (str): The text prompt to send to the GPT model.

    Returns:
    str: The generated note.
    """
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=100
    )
    return response.choices[0].text.strip()

# Process TSV file function
def process_tsv_file(tsv_file):
    """
    Processes a TSV file containing genetic variant data and organizes it by gene.

    Parameters:
    tsv_file (str): Path to the TSV file to be processed.

    Returns:
    dict: A dictionary where keys are gene names and values are lists of variant data.
    """
    variants = defaultdict(list)

    with open(tsv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter='\t')
        for row in reader:
            chromosome = row['chromosome']
            position = row['position']
            allele = row['allele']
            family = row['family']
            symbol = row['symbol'].strip("[]").replace("'", "").split()
            variant_class = row['variant_class']
            note = row['note']
            impact = row['impact']
            max_af = row['max_af']
            gnomadg_af = row['gnomadg_af'].strip("[]").split()

            for gene in symbol:
                variants[gene].append({
                    'chromosome': chromosome,
                    'position': position,
                    'allele': allele,
                    'family': family,
                    'variant_class': variant_class,
                    'note': note,
                    'impact': impact,
                    'max_af': max_af,
                    'gnomadg_af': gnomadg_af
                })

    return variants

# Function to format output with dynamically generated notes
def format_output(variants):
    """
    Formats and prints the variant data for each gene, including generating notes if necessary.

    Parameters:
    variants (dict): A dictionary where keys are gene names and values are lists of variant data.
    """
    for gene, gene_variants in variants.items():
        print(f"{gene} Variants")
        print(f"Chromosome: {gene_variants[0]['chromosome']}")

        alleles = set()
        families = set()
        variant_info = []

        for variant in gene_variants:
            alleles.add(variant['allele'])
            families.add(variant['family'])

            # Uncomment the following lines if using OpenAI API to generate notes
            '''
            if not variant['note']:  # Check if note is empty
                prompt = f"Variant at position {variant['position']} in gene {gene}."
                variant['note'] = generate_note(prompt)  # Generate note using ChatGPT
            '''

            info = f"Variant position: {variant['position']} "
            if variant['family']:
                info += f"a. Family: {variant['family']} "
            if variant['variant_class']:
                info += f"b. Variant class: {variant['variant_class']} "
            if variant['max_af']:
                info += f"c. Max_af: {variant['max_af']} "
            else:
                info += f"c. Max_af: N/A "
            if variant['gnomadg_af']:
                info += f"d. Gnomadg_af: {variant['gnomadg_af'][0]} "
            else:
                info += f"d. Gnomadg_af: N/A "

            variant_info.append(info.strip())

        print(f"Alleles: {', '.join(alleles)}")
        print(f"Families: {', '.join(map(str, families))}")

        print("Types of variants with frequencies:")
        for idx, info in enumerate(variant_info):
            print(f"{info}{' (same variant found in multiple families)' if idx > 0 else ''}")

        print()

# Main function
def main():
    """
    Main function to process the TSV file and format the output.
    """
    tsv_file = '20240701_example_file_v2.xlsx - Sheet1.tsv'
    variants = process_tsv_file(tsv_file)
    format_output(variants)

    document = Document()
    document.add_paragraph(format_output(variants))

    document.save('gen_analysis.docx')


if __name__ == "__main__":
    main()
