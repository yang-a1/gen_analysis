import pandas as pd
import  openai
import numpy as np
from dotenv import load_dotenv
import os
import time

from openai import AzureOpenAI

# Load environment variables from .env file
load_dotenv("/nfs/turbo/umms-mblabns/test/20240809_gpt.env")

""" Example .env file for Umich
model = Model names (gpt-35-turbo, gpt-4, gpt-4o, and etc) API gateway URL = "https://api.umgpt.umich.edu/azure-openai-api"
API VERSION = "2024-06-01" #latest non-preview completion version
DEPLOYMENT_ID = "gpt-35-turbo" #chat deployment model name
API_KEY #your 32 character API key
ORGANIZATION #a valid 6 digit shortcode
"""






# Retrieve the API key from the environment variable
# openai.api_key = os.getenv('OPENAI_API_KEY')

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
        """
        api_key = os.getenv('OPENAI_API_KEY')
        if  api_key is None:
            api_key = os.environ.get('OPENAI_API_KEY', None)
        assert  api_key  is not None, "OpenAI API key not found."
        openai.api_key = api_key
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.7
        )
        content = response.choices[0].message.content.strip()
        return content
        """
        #Create Azure client
        # Amy to decide if she wants os.environ or os.getenv
        client = AzureOpenAI(
            api_key=os.environ['OPENAI_API_KEY'],
            api_version=os.environ['API_VERSION'],
            azure_endpoint = os.environ['openai_api_base'],
            organization = os.environ['OPENAI_organization']
        )

        response = client.chat.completions.create(
                model=os.environ['model'],
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "What is 2 + 2?"}
                ],
                temperature=0,
                max_tokens=150,
                stop=None)
    except openai.error.RateLimitError:
        print("Rate limit exceeded. Waiting for 60 seconds before retrying...")
        time.sleep(60)  # Wait for 60 seconds before retrying
        return generate_elaboration(prompt)
    except openai.error.InvalidRequestError as e:
        print(f"Invalid request: {e}")
        return "Error generating elaboration."
    except openai.error.OpenAIError as e:
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

    # Prepare prompts for elaboration
    mouse_prompt = f"Provide a detailed description of mouse phenotypes associated with {gene_symbol}."
    omim_prompt = f"Provide a detailed description of diseases associated with {gene_symbol} as found in OMIM/GeneCards."

    # Get elaborations from the OpenAI API
    mouse_phenotype_description = generate_elaboration(mouse_prompt)
    omim_description = generate_elaboration(omim_prompt)

    info += f"Gene: {gene_symbol}\n"
    info += f"Mouse phenotype: {mouse_phenotype_description}\n"
    info += f"OMIM/GeneCards: {omim_description}\n"

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

            info += f"\ta. Gnomade allele frequency: {gnomad_af if not pd.isna(gnomad_af) else 'nan'}\n"
            info += f"\tb. Max allele frequency: {max_af}\n"
            info += f"\tc. Amino acid change: {consequence if not pd.isna(consequence) else 'ND'}\n"
            info += f"\td. Polyphen/SIFT: {revel if not pd.isna(revel) else 'ND'}/{sift if not pd.isna(sift) else 'ND'}\n"
            info += f"\te. Effect of amino acid change: {hgvsc if not pd.isna(hgvsc) else 'unknown'}\n"

    return info

def process_file(file_path):
    """
    Processes the TSV file and outputs formatted information.

    Args:
        file_path (str): The path to the TSV file.
    """
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

    dfColumns = list( set(df.columns) & set(columns_of_interest))

    if  len(dfColumns) >0:
        df1 = df[dfColumns]

        # Process each row and print formatted information
        for index, row in df1.iterrows():
            formatted_info = format_variant_info(row)
            print(formatted_info)

    df2 = df[df.columns.difference(dfColumns)]
    print("Additional Information:")
    for index, row in df2.iterrows():
        print(row)


def main():
    file_path = '20240701_example_file_v2.xlsx - TESTER PROMPT.tsv'
    #file_path = '20240701_example_file_v2.xlsx - Sheet1.tsv'
    #file_path = '20240701_example_file_v2.xlsx - BASELINE.tsv'

    # Process the file
    process_file(file_path)

if __name__ == "__main__":
    main()