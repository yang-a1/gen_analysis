import pandas as pd
import  openai
import numpy as np
from dotenv import load_dotenv
import os
import time
from openai import AzureOpenAI
from config import RAW_DATA_DIR, INTERIM_DATA_DIR



# Load environment variables from .env file
load_dotenv("/nfs/turbo/umms-mblabns/test/20240816_amy_gpt.env")

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
    # Get all .tsv files from RAW_DATA_DIR
    tsv_files = get_files_in_folder(RAW_DATA_DIR)


    for file_path in tsv_files:
        process_file(file_path)

if __name__ == "__main__":
    main()

