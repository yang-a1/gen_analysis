import pandas as pd
import openai
import numpy as np
import os
import time
import json
import re
import logging
from collections import OrderedDict
from dotenv import load_dotenv, find_dotenv
from openai import AzureOpenAI

# Import your own modules and configuration
from gen_analysis_module.config import (
    RAW_DATA_DIR, INTERIM_DATA_DIR, PROCESSED_DATA_DIR, PROJ_ROOT,
    PROMPTS_JSON_PATH, ENV_FILE_PATH, MAX_TOKENS_VALUE, TEMPERATURE_VALUE,
    CSS_CONTENT
)
from gen_analysis_module.convert_md_html_pdf import markdown_to_html, complete_html_pdf

# Load environment variables from .env file
load_dotenv(find_dotenv(ENV_FILE_PATH))

# Define the path to the variant description JSON (adjust as needed)
VARIANT_DESCRIPTION_JSON_PATH = os.path.join(PROJ_ROOT, "variant_description.json")

def load_prompts(json_path):
    """
    Loads prompts from a JSON file. Returns an empty dictionary if the file is missing or empty.
    """
    if not json_path or not os.path.exists(json_path):
        return {}
    try:
        with open(json_path, 'r') as file:
            return json.load(file, object_pairs_hook=OrderedDict)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Warning: Could not load prompts from {json_path}. Error: {e}")
        return {}

def load_variant_description(json_path):
    """
    Loads the variant description configuration from a JSON file.
    Returns an ordered dictionary so that the fields are printed in a predictable order.
    """
    if not json_path or not os.path.exists(json_path):
        return OrderedDict()
    try:
        with open(json_path, 'r') as file:
            return json.load(file, object_pairs_hook=OrderedDict)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Warning: Could not load variant description config from {json_path}. Error: {e}")
        return OrderedDict()

def create_prompts(prompts, gene_symbol):
    """
    Create dynamic prompts by replacing the gene symbol placeholder.
    """
    if not prompts:
        return OrderedDict()
    return OrderedDict((key, value.format(gene_symbol=gene_symbol)) for key, value in prompts.items())

def md_name_creator(file_path):
    """
    Create a markdown file name from the file path.
    """
    md_output_filename = f"{time.strftime('%Y%m%dT%H%M')}_{os.path.basename(file_path)}_output.md"
    md_output_filepath = os.path.join(PROCESSED_DATA_DIR, md_output_filename)
    return md_output_filepath

def safe_get(row, key):
    """Return the value from the row for the given key or 'N/A' if missing."""
    return row.get(key, 'N/A')

def process_file(file_path, prompts, variant_desc_config, max_lines=1000):
    """
    Processes the TSV file, formats variant information, and writes two markdown files:
    1. One with family tables.
    2. One without family tables (if applicable).
    """
    # Check the number of lines first
    with open(file_path, 'r') as f:
        line_count = sum(1 for _ in f)
    if line_count > max_lines:
        print(f"Error: {file_path} is too long. Cannot exceed {max_lines} lines.")
        return None, None

    # Read the TSV file into a DataFrame
    df = pd.read_csv(file_path, sep='\t')
    
    # Instead of filtering for specific columns, we simply check if the DataFrame is empty.
    if df.empty or len(df.columns) == 0:
        print(f"Warning: Nothing to process in {file_path}")
        return None, None

    # (Optional) You might want to rename or clean the columns if necessary.
    df_filtered = df.copy()

    # Determine if there is family information by checking for columns containing any family-related string.
    members = [
        "child", "father", "mother", "affectedF", "affectedF1", "affectedF2",
        "affectedM", "affectedM1", "affectedM2", "affectedM3", "alias",
        "childAF1", "childAF2", "childF", "childM", "childUF1", "father",
        "individualM", "unaffectedF"
    ]
    family_related_strings = ["short alt observations", "read depth", "allele frequency"]
    column_members = [col for col in df_filtered.columns if any(fr in col.lower() for fr in family_related_strings)]
    family_members_from_columns = [col.split(":")[0] for col in column_members]
    members += family_members_from_columns
    family_related_columns = [col for col in df_filtered.columns if any(fm.lower() in col.lower() for fm in members)]
    has_family_info = bool(family_related_columns)

    # Define output markdown file paths
    md_output_filename = f"{time.strftime('%Y%m%dT%H%M')}_{os.path.basename(file_path)}_output.md"
    md_output_filepath = os.path.join(PROCESSED_DATA_DIR, md_output_filename)
    md_output_filename_no_family = f"{time.strftime('%Y%m%dT%H%M')}_{os.path.basename(file_path)}_output_no_family.md"
    md_output_filepath_no_family = os.path.join(PROCESSED_DATA_DIR, md_output_filename_no_family)

    print(f"Processing {file_path} -> {md_output_filepath}")

    with open(md_output_filepath, 'w') as f:
        f.write(f"# {os.path.basename(file_path)}\n=================\n\n")
        for _, row in df_filtered.iterrows():
            formatted_info = format_variant_info(row, prompts, variant_desc_config, include_family=True)
            if formatted_info:
                f.write(formatted_info + "\n")

    if has_family_info:
        print(f"Processing without family tables -> {md_output_filepath_no_family}")
        with open(md_output_filepath_no_family, 'w') as f:
            f.write(f"# {os.path.basename(file_path)} (No Family Info)\n=================\n\n")
            for _, row in df_filtered.iterrows():
                formatted_info = format_variant_info(row, prompts, variant_desc_config, include_family=False)
                if formatted_info:
                    f.write(formatted_info + "\n")
    else:
        md_output_filepath_no_family = None

    return md_output_filepath, md_output_filepath_no_family

def format_variant_info(row, prompts, variant_desc_config, include_family=True):
    """
    Format variant information into a markdown table, with an option to exclude family tables.
    The variant description fields (and their labels) are defined entirely in the provided JSON file.
    For any key that isn't found in the row, 'N/A' is used.
    """
    # Retrieve the gene symbol (allowing for list type)
    gene_symbol = safe_get(row, 'symbol')
    if isinstance(gene_symbol, list):
        gene_symbol = gene_symbol[0] if gene_symbol else 'N/A'
    
    if not re.search("[A-Za-z0-9]", gene_symbol):
        logging.warning(f"Invalid gene symbol '{gene_symbol}'.")
        return None

    elaborations = generate_elaborations_for_prompts(prompts, gene_symbol)
    
    # Start the variant description with a header using the allele
    allele = safe_get(row, 'allele')
    variant_description = f"1. Variant description for {allele}:\n"

    # Iterate over the variant description configuration in order.
    # The keys in the JSON file determine which fields to print,
    # and their values provide the description (label) to print.
    letter = ord('a')
    for key, description in variant_desc_config.items():
        value = safe_get(row, key)
        variant_description += f"\t{chr(letter)}. {description}: {value}\n"
        letter += 1

    if include_family:
        family_table_section = create_family_tables(row)
        return elaborations + variant_description + "\n" + family_table_section + "\n"
    else:
        return elaborations + variant_description + "\n"

def create_family_tables(row):
    """
    Create separate markdown tables for family members (e.g., child, father, mother).
    This function dynamically builds tables based on available columns.
    """
    family_members = [
        "child", "father", "mother", "affectedF", "affectedF1", "affectedF2",
        "affectedM", "affectedM1", "affectedM2", "affectedM3", "alias",
        "childAF1", "childAF2", "childF", "childM", "childUF1", "father",
        "individualM", "unaffectedF"
    ]

    tables = []
    for family_member in family_members:
        # Find all columns starting with the family member name (case-insensitive)
        family_columns = [col for col in row.index if col.lower().startswith(family_member.lower())]
        if family_columns:
            table_header = f"### {family_member.capitalize()} Information"
            table = "| Attribute                          | Value                          |\n"
            table += "|------------------------------------|--------------------------------|\n"
            for column in family_columns:
                table += f"| {column:<34} | {row[column]:<30} |\n"
            tables.append(table_header + "\n" + table)
    return "\n\n".join(tables)

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

def generate_elaboration(prompt):
    """
    Generates elaboration text using the OpenAI API with a retry mechanism.
    """
    try:
        client = AzureOpenAI(
            api_key=os.environ['OPENAI_API_KEY'],
            api_version=os.environ['API_VERSION'],
            azure_endpoint=os.environ['openai_api_base'],
            organization=os.environ['OPENAI_organization']
        )

        response = client.chat.completions.create(
            model=os.environ['model'],
            messages=[
                {"role": "system", "content": "You are a professional and concise assistant."},
                {"role": "user", "content": prompt}
            ],
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

def main():
    prompts = load_prompts(PROMPTS_JSON_PATH)
    variant_desc_config = load_variant_description(VARIANT_DESCRIPTION_JSON_PATH)

    tsv_files = [
        os.path.join(RAW_DATA_DIR, file)
        for file in os.listdir(RAW_DATA_DIR) if file.endswith(".tsv")
    ]

    for file_path in tsv_files:
        md_file_path, md_file_path_no_family = process_file(file_path, prompts, variant_desc_config)
        print(md_file_path)
        complete_html_pdf(md_file_path, CSS_CONTENT, PROMPTS_JSON_PATH)
        if md_file_path_no_family:
            print(md_file_path_no_family)
            complete_html_pdf(md_file_path_no_family, CSS_CONTENT, PROMPTS_JSON_PATH)

if __name__ == "__main__":
    main()
