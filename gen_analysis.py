import csv
import os
from collections import defaultdict
import openai  # Make sure to install this library: pip install openai
from dotenv import load_dotenv, find_dotenv # Make sure to install this library: pip install python-dotenv
from prettytable import PrettyTable

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

# Function to display variant description in a table
def display_variant_table(gene, gene_variants):
    table = PrettyTable()
    table.field_names = ["Variant Description", "Details"]

    for variant in gene_variants:
        table.add_row(["Chromosome", variant['chromosome']])
        table.add_row(["Position", variant['position']])
        table.add_row(["Allele", variant['allele']])
        table.add_row(["Family", variant.get('family', 'N/A')])
        table.add_row(["Variant Class", variant.get('variant_class', 'N/A')])
        table.add_row(["Amino Acid Change", variant.get('impact', 'N/A')])
        table.add_row(["Gnomad Allele Frequency", ", ".join(variant.get('gnomadg_af', ['N/A']))])
        table.add_row(["Max Allele Frequency", variant.get('max_af', 'N/A')])
        table.add_row(["Polyphen/SIFT", variant.get('note', 'N/A')])

    print(f"\n{gene} Variants Table:\n")
    print(table)

# Function to format output with dynamically generated notes
def format_output(variants):
    for gene, gene_variants in variants.items():
        # Display gene and chromosome information
        print(f"\n{gene} Variants")
        print(f"Chromosome: {gene_variants[0]['chromosome']}")

        # Gather unique alleles and families
        alleles = {variant['allele'] for variant in gene_variants}
        families = {variant['family'] for variant in gene_variants}

        # Print alleles and families
        print(f"Alleles: {', '.join(alleles)}")
        print(f"Families: {', '.join(map(str, families))}")

        # Display detailed table of variants for the gene
        display_variant_table(gene, gene_variants)

        # Variant details in summary format
        print("\nTypes of variants with frequencies:")
        seen_positions = set()
        for idx, variant in enumerate(gene_variants):
            position = variant['position']
            family = variant.get('family', 'N/A')
            variant_class = variant.get('variant_class', 'N/A')
            max_af = variant.get('max_af', 'N/A')
            gnomad_af = variant.get('gnomadg_af', ['N/A'])[0]

            # Summary string for the variant
            variant_summary = (
                f"Variant position: {position} "
                f"a. Family: {family} "
                f"b. Variant class: {variant_class} "
                f"c. Max_af: {max_af} "
                f"d. Gnomadg_af: {gnomad_af}"
            )

            # Mark duplicates based on position
            duplicate_note = " (same variant found in multiple families)" if position in seen_positions else ""
            seen_positions.add(position)

            # Print the summary for the variant
            print(f"{variant_summary}{duplicate_note}")

        print()  # Add blank line for better readability

# Main function (assuming it's defined elsewhere)
def main():
    tsv_file = '20240701_example_file_v2.xlsx - Sheet1.tsv'
    variants = process_tsv_file(tsv_file)
    format_output(variants)

if __name__ == "__main__":
    main()