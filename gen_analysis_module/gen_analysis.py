import pandas as pd
import  openai
import numpy as np
from dotenv import load_dotenv, find_dotenv
import os
import time
from openai import AzureOpenAI
from gen_analysis_module.config import RAW_DATA_DIR, INTERIM_DATA_DIR, PROCESSED_DATA_DIR
import json
import re
import logging

# Load prompts from the JSON configuration file
def load_prompts(json_path):
    with open(json_path, 'r') as file:
        prompts = json.load(file)
    return prompts

# Load prompts at the beginning of your script
# TODO: Update the path to the prompts.json file as a path in the config.py file
prompts = load_prompts('prompts.json')

# Load environment variables from .env file
# this enviroment file should be in the root of the project
load_dotenv(find_dotenv("gen_analysis.env"))
# load_dotenv(find_dotenv(os.getcwd()))

def get_files_in_folder(folder_path):
    """
    Get all the tsv files in a specified folder and create a list of the full path.

    Args:
        folder_path (str): The path to the folder.

    Returns:
        list: A list of full paths to the files in the folder.
    """
    file_paths = []
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        if os.path.isfile(file_path) and file.endswith(".tsv"):
            file_paths.append(file_path)
    return file_paths


def read_tsv(file_path):
    """
    Reads a TSV file into a DataFrame.

    Args:
        file_path (str): The path to the TSV file.

    Returns:
        pd.DataFrame: A DataFrame containing the data from the TSV file.
    """
    return pd.read_csv(file_path, sep='\t')

def generate_elaboration(prompt):
    """
    Generates elaboration text using the OpenAI API with the gpt-3.5-turbo model.

    Args:
        prompt (str): The prompt to be sent to the OpenAI API.

    Returns:
        str: The generated elaboration text.

    Raises:
        openai.error.RateLimitError: If rate limit is exceeded, waits and retries.
        openai.error.InvalidRequestError: If the request is invalid.
        openai.error.OpenAIError: For general OpenAI API errors.
        Exception: For unexpected errors.
    """
    try:
        client = AzureOpenAI(
            api_key=os.environ['OPENAI_API_KEY'],
            api_version=os.environ['API_VERSION'],
            azure_endpoint = os.environ['openai_api_base'],
            organization = os.environ['OPENAI_organization'])


        response = client.chat.completions.create(
            model="gpt-35-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.7
        )
        content = response.choices[0].message.content.strip()
        return content
    except client.error.RateLimitError:
        print("Rate limit exceeded. Waiting for 60 seconds before retrying...")
        time.sleep(60)  # Wait for 60 seconds before retrying
        return generate_elaboration(prompt)
    except client.error.InvalidRequestError as e:
        print(f"Invalid request: {e}")
        return "Error generating elaboration."
    except client.error.OpenAIError as e:
        print(f"OpenAI API error: {e}")
        return "Error generating elaboration."
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return "Error generating elaboration."

def format_variant_info(row):
    """
    Formats the variant information from a DataFrame row into a human-readable string.

    Args:
        row (pd.Series): A row from the DataFrame containing genetic variant information.

    Returns:
        str: Formatted variant information.
    """
    info = ""

    # Extract gene symbol
    gene_symbol = row['symbol'][0] if isinstance(row['symbol'], list) else row['symbol']

    logging.basicConfig(filename='invalid_gene_symbols.log', level=logging.WARNING,
                    format='%(asctime)s - %(levelname)s - %(message)s')

    if not re.search("[A-Za-z0-9]", gene_symbol):
        logging.warning(f"Invalid gene symbol '{gene_symbol}'. Gene symbols must contain at least one letter or number.")
        return None

    # Prepare prompts for elaboration using the loaded configuration
    mouse_prompt = prompts['mouse_prompt'].format(gene_symbol=gene_symbol)
    omim_prompt = prompts['omim_prompt'].format(gene_symbol=gene_symbol)

    # Get elaborations from the OpenAI API
    mouse_phenotype_description = generate_elaboration(mouse_prompt)
    omim_description = generate_elaboration(omim_prompt)

    info += f"# Gene: {gene_symbol}\n"
    info += f"## Mouse phenotype: \n{mouse_phenotype_description}\n"
    info += f"## OMIM/GeneCards: \n{omim_description}\n"

    # Extract alternative alleles
    if 'alternative allele' in row and pd.notna(row['alternative allele']):
        alleles = row['alternative allele']
        if isinstance(alleles, str):
            alleles = alleles.split(',')  # Assuming comma-separated
        elif not isinstance(alleles, list):
            alleles = [alleles]

        for i, allele in enumerate(alleles):
            info += f"{i+1}. Variant description for {allele} (details):\n"
            gnomad_af = row['gnomad genome af'][0] if isinstance(row['gnomad genome af'], list) else row['gnomad genome af']
            max_af = row['max_af'] if pd.notna(row['max_af']) else 'nan'
            consequence = row['consequence'][0] if isinstance(row['consequence'], list) else row['consequence']
            revel = row['revel'][0] if isinstance(row['revel'], list) else row['revel']
            sift = row['sift'][0] if isinstance(row['sift'], list) else row['sift']
            hgvsc = row['hgvsc'][0] if isinstance(row['hgvsc'], list) else row['hgvsc']
            hgvsp = row['hgvsp'][0] if isinstance(row['hgvsp'], list) else row['hgvsp']

            # contains  ": allele frequency" where this is a value.

            info += f"\ta. Amino acid change: {consequence if not pd.isna(consequence) else 'ND'}\n"
            info += f"\tb. Gnomade allele frequency: {gnomad_af if not pd.isna(gnomad_af) else 'nan'}\n"
            info += f"\tc. Max allele frequency: {max_af}\n"
            info += f"\td. Polyphen/SIFT: {revel if not pd.isna(revel) else 'ND'}/{sift if not pd.isna(sift) else 'ND'}\n"
            info += f"\te. Effect of amino acid change: {hgvsp if not pd.isna(hgvsp) else 'unknown'}\n"
            info += f"\tf. The hgvsg information of the change: {hgvsc if not pd.isna(hgvsc) else 'unknown'}\n"




    return info

def process_file(file_path, max_lines=1000):
    """
    Processes the TSV file and outputs formatted information.

    Args:
        file_path (str): The path to the TSV file.
    """
    with open(file_path, 'r') as f:
        line_count = sum(1 for _ in f)
    if line_count > max_lines:
        print(f"Error: {file_path} is too long. Cannot exceed 1000 lines.")
        return

    df = read_tsv(file_path)

    # Extract necessary columns (adjust as needed based on your data)
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

    dfColumns = list(set(df.columns) & set(columns_of_interest))

    if len(dfColumns) > 0:
        df1 = df[dfColumns]

        # Change the timestamp format to YYYYMMDDThhmm
        md_output_filename = f"{time.strftime('%Y%m%dT%H%M')}_{os.path.basename(file_path)}_output.md"
        md_output_filepath = os.path.join(PROCESSED_DATA_DIR, md_output_filename)
        print(md_output_filepath)

        # Create a file at md_output_filepath and write the header to it
        with open(md_output_filepath, 'w') as f:
            header = f"# {os.path.basename(file_path)}\n\n"
            header += "=================\n\n"
            f.write(header)

        # Loop through each row in the DataFrame and write the formatted information
        for index, row in df1.iterrows():
            formatted_info = format_variant_info(row)
            f.write(formatted_info + "\n")  # Write the formatted info to the markdown file

    df2 = df[df.columns.difference(dfColumns)]

    # TODO: Reformat the additional information so that it is readable in markdown format
    # You can further process df2 as needed for additional information
    # print("Additional Information:")
    # for index, row in df2.iterrows():
    #    print(row)



def main():
    # Get all .tsv files from RAW_DATA_DIR
    tsv_files = get_files_in_folder(RAW_DATA_DIR)


    for file_path in tsv_files:
        process_file(file_path)

if __name__ == "__main__":
    main()


