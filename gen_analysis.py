import csv
import os
from collections import defaultdict
import openai  # Make sure to install this library: pip install openai
from dotenv import load_dotenv, find_dotenv # Make sure to install this library: pip install python-dotenv

# load the .env file and get the OpenAI API Key from .env file
_ = load_dotenv(find_dotenv())
openai.api_key = os.environ.get('OPENAI_API_KEY')

# Function to generate notes using ChatGPT
def generate_note(prompt):
    
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=100
    )
    
    return response.choices[0].text.strip()

# Process TSV file function (assuming it's defined elsewhere)
def process_tsv_file(tsv_file):
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
    for gene, gene_variants in variants.items():
        print(f"{gene} Variants")
        print(f"Chromosome: {gene_variants[0]['chromosome']}")

        alleles = set()
        families = set()
        variant_info = []

        for variant in gene_variants:
            alleles.add(variant['allele'])
            families.add(variant['family'])
            '''
            # comment out the following part b/c it is not compatible with openai ver >=1.00
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




# Main function (assuming it's defined elsewhere)
def main():
    tsv_file = '20240701_example_file_v2.xlsx - Sheet1.tsv'
    variants = process_tsv_file(tsv_file)
    format_output(variants)

if __name__ == "__main__":
    main()