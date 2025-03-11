import pandas as pd
import openai
import numpy as np
from dotenv import load_dotenv, find_dotenv
import os
import time
from openai import AzureOpenAI
from gen_analysis_module.config import RAW_DATA_DIR, INTERIM_DATA_DIR, PROCESSED_DATA_DIR, PROJ_ROOT, PROMPTS_JSON_PATH, ENV_FILE_PATH, MAX_TOKENS_VALUE, TEMPERATURE_VALUE, CSS_CONTENT, VARIANT_DESCRIPTION_PATH, FAMILY_MEMBERS_PATH
import json
import re
import logging
from collections import OrderedDict
from gen_analysis_module.convert_md_html_pdf import markdown_to_html, complete_html_pdf

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

# Load variant description mapping from JSON
def load_variant_description(json_path):
    """
    Load the variant description JSON file.
    """
    if not os.path.exists(json_path):
        print(f"Warning: {json_path} not found.")
        return {}

    try:
        with open(json_path, 'r') as file:
            return json.load(file)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading {json_path}: {e}")
        return {}

# Load family members from JSON
def load_family_members(json_path):
    """
    Load the family members list from a JSON file.
    """
    if not os.path.exists(json_path):
        print(f"Warning: {json_path} not found. Using default values.")
        return {
            "members": [],
            "family_related_strings": []
        }

    try:
        with open(json_path, 'r') as file:
            return json.load(file)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading {json_path}: {e}")
        return {
            "members": [],
            "family_related_strings": []
        }

# Normalize column names for flexible matching
def normalize_column_name(name):
    """
    Normalize column names by removing spaces, dashes, underscores, and converting to lowercase.
    """
    return re.sub(r'[\s\-_]', '', name.lower())

# Match TSV columns with JSON fields
def find_matching_column(json_key, tsv_columns):
    """
    Find the best match for a JSON key in the TSV columns using normalization.
    """
    normalized_json_key = normalize_column_name(json_key)
    normalized_columns = {normalize_column_name(col): col for col in tsv_columns}

    return normalized_columns.get(normalized_json_key, None)

# TODO: add this function to process_file to define the name outside of the function
def md_name_creator(file_path):
    """
    Create a markdown file name from the file path.
    """
    md_output_filename = f"{time.strftime('%Y%m%dT%H%M')}_{os.path.basename(file_path)}_output.md"
    md_output_filepath = os.path.join(PROCESSED_DATA_DIR, md_output_filename)
    return md_output_filepath

# Process files and format variant information
def process_file(file_path, prompts, variant_descriptions, family_members_json, max_lines=1000):
    """
    Processes the TSV file, formats variant information, and writes two markdown files:
    1. One with family tables.
    2. One without family tables (if applicable).
    """
    with open(file_path, 'r') as f:
        line_count = sum(1 for _ in f)
    if line_count > max_lines:
        print(f"Error: {file_path} is too long. Cannot exceed 1000 lines.")
        return None, None

    df = pd.read_csv(file_path, sep='\t')

    # Keep all columns of interest
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
        return None, None

    df_filtered = df[df_columns]

    members = family_members_json["members"]
    family_related_strings = family_members_json.get("family_related_strings", [])

    # Detect columns with family-related data
    column_members = [col for col in df_filtered.columns if any(fam_str in col.lower() for fam_str in family_related_strings)]
    family_members = [col.split(":")[0] for col in column_members]
    members += family_members

    family_related_columns = [col for col in df_filtered.columns if any(member in col.lower() for member in members)]
    has_family_info = bool(family_related_columns)

    # Define output file names
    md_output_filename = f"{time.strftime('%Y%m%dT%H%M')}_{os.path.basename(file_path)}_output.md"
    md_output_filepath = os.path.join(PROCESSED_DATA_DIR, md_output_filename)

    md_output_filename_no_family = f"{time.strftime('%Y%m%dT%H%M')}_{os.path.basename(file_path)}_output_no_family.md"
    md_output_filepath_no_family = os.path.join(PROCESSED_DATA_DIR, md_output_filename_no_family)

    print(f"Processing {file_path} -> {md_output_filepath}")

    with open(md_output_filepath, 'w') as f:
        f.write(f"# {os.path.basename(file_path)}\n=================\n\n")
        for _, row in df_filtered.iterrows():
            formatted_info = format_variant_info(row, prompts, variant_descriptions, family_members_json, include_family=True)
            if formatted_info:
                f.write(formatted_info + "\n")

    if has_family_info:
        print(f"Processing without family tables -> {md_output_filepath_no_family}")
        with open(md_output_filepath_no_family, 'w') as f:
            f.write(f"# {os.path.basename(file_path)} (No Family Info)\n=================\n\n")
            for _, row in df_filtered.iterrows():
                formatted_info = format_variant_info(row, prompts, variant_descriptions, family_members_json, include_family=False)
                if formatted_info:
                    f.write(formatted_info + "\n")
    else:
        md_output_filepath_no_family = None

    return md_output_filepath, md_output_filepath_no_family

def safe_get(row, key):
    """Return the value from the row for the given key or 'N/A' if missing."""
    return row.get(key, 'N/A')

# Extracts and formats variant information with PrettyTable integration
def format_variant_info(row, prompts, variant_descriptions, family_members_json, include_family=True):
    """
    Format variant information dynamically using the preloaded variant_description.json mappings.
    """
    gene_symbol = row.get('symbol', 'N/A')
    if isinstance(gene_symbol, list):
        gene_symbol = gene_symbol[0] if gene_symbol else 'N/A'
    
    if not re.search("[A-Za-z0-9]", gene_symbol):
        logging.warning(f"Invalid gene symbol '{gene_symbol}'.")
        return None

    elaborations = generate_elaborations_for_prompts(prompts, gene_symbol)

    variant_description_text = ["## Variant Description"]

    if variant_descriptions:
        for json_key, description in variant_descriptions.items():
            matched_column = find_matching_column(json_key, row.index)
            
            if matched_column:
                value = safe_get(row, matched_column)
            else:
                value = "**Could not find information from TSV file**"

            variant_description_text.append(f"- **{description}**: {value}")

    else:
        variant_description_text.append("No variant description available.")

    variant_description_text = "\n".join(variant_description_text)

    family_table_section = ""
    if include_family:
        family_table_section = create_family_tables(row, family_members_json)

    return elaborations + "\n\n" + variant_description_text + "\n\n" + family_table_section + "\n"

def create_family_tables(row, family_members_json):
    """
    Create separate tables for family members (e.g., child, father, mother).
    This function dynamically builds tables based on available columns.
    """
    family_members = set(family_members_json.get("members", []))
    tables = []
    seen_members = set()  # Track already added members

    for family_member in family_members:
        family_columns = [col for col in row.index if col.lower().startswith(family_member.lower())]

        if family_columns and family_member not in seen_members:
            seen_members.add(family_member)

            table_header = f"### {family_member.capitalize()} Information"
            table = "| Attribute                          | Value                          |\n"
            table += "|------------------------------------|--------------------------------|\n"

            for column in family_columns:
                value = safe_get(row, column)
                if value == "N/A":
                    value = "**Could not find information**"

                table += f"| {column:<34} | {value:<30} |\n"

            tables.append(table_header + "\n" + table)

    return "\n\n".join(tables)

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
    variant_descriptions = load_variant_description(VARIANT_DESCRIPTION_PATH)
    family_members_json = load_family_members(FAMILY_MEMBERS_PATH)

    tsv_files = [os.path.join(RAW_DATA_DIR, file) for file in os.listdir(RAW_DATA_DIR) if file.endswith(".tsv")]

    for file_path in tsv_files:
        md_file_path, md_file_path_no_family = process_file(
            file_path, prompts, variant_descriptions, family_members_json
        )

        print(md_file_path)
        complete_html_pdf(md_file_path, CSS_CONTENT, PROMPTS_JSON_PATH)

        if md_file_path_no_family:
            print(md_file_path_no_family)
            complete_html_pdf(md_file_path_no_family, CSS_CONTENT, PROMPTS_JSON_PATH)

if __name__ == "__main__":
    main()
