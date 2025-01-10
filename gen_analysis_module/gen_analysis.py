import pandas as pd
import openai
import numpy as np
from dotenv import load_dotenv, find_dotenv
import os
import time
from openai import AzureOpenAI
from gen_analysis_module.config import RAW_DATA_DIR, INTERIM_DATA_DIR, PROCESSED_DATA_DIR, PROJ_ROOT, PROMPTS_JSON_PATH, ENV_FILE_PATH, MAX_TOKENS_VALUE, TEMPERATURE_VALUE
import json
import re
import logging
from collections import OrderedDict
from prettytable import PrettyTable

# Load environment variables from .env file
load_dotenv(find_dotenv(ENV_FILE_PATH))

# Load prompts from the JSON configuration file
def load_prompts(json_path):
    """
    Loads prompts from a JSON file. Returns an empty dictionary if the file is missing or empty.
    """
    if not json_path or not os.path.exists(json_path):
        return {}  # Return an empty dictionary if the file is missing or empty

    try:
        with open(json_path, 'r') as file:
            return json.load(file)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Warning: Could not load prompts from {json_path}. Error: {e}")
        return {}

# Dynamically create prompts from a dictionary and replace the gene symbol placeholder
def create_prompts(prompts, gene_symbol):
    """
    Create dynamic prompts by replacing the gene symbol placeholder.
    """
    if not prompts:
        return OrderedDict()

    return OrderedDict((key, value.format(gene_symbol=gene_symbol)) for key, value in prompts.items())

# Process files and format variant information
def process_file(file_path, prompts, max_lines=1000):
    """
    Processes the TSV file, formats variant information, and writes to markdown.
    """
    with open(file_path, 'r') as f:
        line_count = sum(1 for _ in f)
    if line_count > max_lines:
        print(f"Error: {file_path} is too long. Cannot exceed 1000 lines.")
        return

    df = pd.read_csv(file_path, sep='\t')

    columns_of_interest = [
        'chromosome', 'position', 'allele', 'family', 'symbol', 'variant_class', 'impact',
        'gnomadg_af', 'max_af', 'child: allele frequency', 'father: allele frequency', 'mother: allele frequency',
        'child: short alt observations', 'father: short alt observations', 'mother: short alt observations',
        'child: read depth', 'father: read depth', 'mother: read depth', 'filename',
        'prob: absent', 'prob: artifact', 'prob: denovo_child', 'prob: inherited',
        'abs_ref_alt_diff', 'alternative allele', 'clinical significance', 'existing_variation',
        'hgvsg', 'var_type', 'consequence', 'feature', 'feature_type', 'gene', 'gnomad genome af',
        'hgvsc', 'hgvsp', 'revel', 'sift', 'strand', 'uniparc', 'symbol_list', 'gene_list'
    ]

    df_columns = list(set(df.columns) & set(columns_of_interest))
    if len(df_columns) == 0:
        print(f"Warning: No relevant columns in {file_path}")
        return

    df_filtered = df[df_columns]

    md_output_filename = f"{time.strftime('%Y%m%dT%H%M')}_{os.path.basename(file_path)}_output.md"
    md_output_filepath = os.path.join(PROCESSED_DATA_DIR, md_output_filename)
    print(f"Processing {file_path} -> {md_output_filepath}")

    with open(md_output_filepath, 'w') as f:
        f.write(f"# {os.path.basename(file_path)}\n=================\n\n")
        for _, row in df_filtered.iterrows():
            formatted_info = format_variant_info(row, prompts)
            if formatted_info:
                f.write(formatted_info + "\n")

# Extracts and formats variant information with PrettyTable integration
# Extracts and formats variant information with PrettyTable integration
def format_variant_info(row, prompts):
    """
    Format variant information into a markdown table, separating list-based attributes from others.
    """
    gene_symbol = row['symbol'][0] if isinstance(row['symbol'], list) else row['symbol']

    # Log any invalid gene symbols
    if not re.search("[A-Za-z0-9]", gene_symbol):
        logging.warning(f"Invalid gene symbol '{gene_symbol}'. Gene symbols must contain at least one letter or number.")
        return None

    # Generate elaborations dynamically for the gene symbol
    elaborations = generate_elaborations_for_prompts(prompts, gene_symbol)

    # Create the Variant description section with list-based attributes
    variant_description = f"1. Variant description for {row['allele']} (details):\n"
    variant_description += f"\ta. Amino acid change: {row.get('impact', 'ND')}\n"
    variant_description += f"\tb. Gnomad allele frequency: {row.get('gnomadg_af', 'nan')}\n"
    variant_description += f"\tc. Max allele frequency: {row.get('max_af', 'nan')}\n"
    variant_description += f"\td. Polyphen/SIFT: {row.get('revel', 'ND')} / {row.get('sift', 'ND')}\n"

    table = "Additional Variant Information"
    # Start creating the markdown table for other attributes that aren't in the description above
    table = "| Additional Attribute              | Value                          |\n"
    table += "|------------------------|--------------------------------|\n"

    # Attributes to exclude from the table (because they are in the variant description above)
    exclude_attributes = ['impact', 'gnomadg_af', 'max_af', 'revel', 'sift']

    # Loop through all columns and include the ones not excluded
    for attribute, value in row.items():
        # Check if the attribute is not in the exclude list and is not a list itself
        if attribute not in exclude_attributes and not isinstance(value, list):
            table += f"| {attribute:<22} | {value:<30} |\n"

    # Make sure to add a newline at the end of the variant description and the table for formatting
    return elaborations + variant_description + "\n" + table + "\n"

# Generate elaborations for all prompts
def generate_elaborations_for_prompts(prompts, gene_symbol):
    """
    Generate elaborations for all prompts dynamically.
    """
    elaborations = f"# Gene: {gene_symbol}\n"
    if prompts:
        for key, value in create_prompts(prompts, gene_symbol).items():
            elaboration = generate_elaboration(value)
            elaborations += f"## {key.replace('_', ' ').capitalize()}: \n{elaboration}\n"
    return elaborations

# Generate elaboration using OpenAI API (with retry mechanism)
def generate_elaboration(prompt):
    """
    Generates elaboration text using the OpenAI API with retry mechanism.
    """
    try:
        client = AzureOpenAI(
            api_key=os.environ['OPENAI_API_KEY'],
            api_version=os.environ['API_VERSION'],
            azure_endpoint=os.environ['openai_api_base'],
            organization=os.environ['OPENAI_organization'])

        response = client.chat.completions.create(
            model=os.environ['model'],
            messages=[{"role": "system", "content": "You are a professional and concise assistant."}, {"role": "user", "content": prompt}],
            max_tokens=MAX_TOKENS_VALUE,
            temperature=TEMPERATURE_VALUE
        )

        elaboration = response.choices[0].message.content.strip()

        if not elaboration or elaboration.lower().startswith("i'm sorry"):
            elaboration = "No relevant elaboration found for this gene symbol."

        return elaboration

    except client.error.RateLimitError:
        print("Rate limit exceeded. Retrying in 60 seconds...")
        time.sleep(60)
        return generate_elaboration(prompt)
    except client.error.OpenAIError as e:
        print(f"OpenAI API error: {e}")
        return "Error generating elaboration."
    except Exception as e:
        print(f"Unexpected error: {e}")
        return "Error generating elaboration."

# Main function to process all files in the raw data directory
def main():
    prompts = load_prompts(PROMPTS_JSON_PATH)
    tsv_files = [os.path.join(RAW_DATA_DIR, file) for file in os.listdir(RAW_DATA_DIR) if file.endswith(".tsv")]

    for file_path in tsv_files:
        process_file(file_path, prompts)

if __name__ == "__main__":
    main()
