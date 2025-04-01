import pandas as pd
import os
import openai
from openai import AzureOpenAI
from dotenv import load_dotenv, find_dotenv
import re

load_dotenv(find_dotenv("gen_analysis.env"))  # Load .env file

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
API_VERSION = os.getenv('API_VERSION')
OPENAI_ORG = os.getenv('OPENAI_organization')
OPENAI_ENDPOINT = os.getenv('openai_api_base')
# print the API_version, OPENAI_ORG, OPENAI_ENDPOINT
print(f"API_VERSION: {API_VERSION}")
print(f"OPENAI_ORG: {OPENAI_ORG}")
print(f"OPENAI_ENDPOINT: {OPENAI_ENDPOINT}")
# print the model name


if not all([OPENAI_API_KEY, API_VERSION, OPENAI_ORG, OPENAI_ENDPOINT]):
    raise ValueError("ERROR: One or more OpenAI credentials are missing. Check your .env file.")

client = AzureOpenAI(
    api_key=OPENAI_API_KEY,
    api_version=API_VERSION,
    azure_endpoint=OPENAI_ENDPOINT,
    organization=OPENAI_ORG
)
api_version="2025-03-01-preview"
file_path = "references/Chicago_Ataxia_Exome_Gene_List.tsv"

if not os.path.exists(file_path):
    raise FileNotFoundError(f"ERROR: File '{file_path}' not found. Ensure the path is correct.")

df = pd.read_csv(file_path, sep="\t")
# df = pd.read_csv(file_path, sep="\t", nrows=50)  # For testing, read only the first 50 rows
# take only the first 50 rows for testing
# take only with the following string in the name
# df = df[df['symbol'].str.contains('AMACR|APOB|ARL3|ARL6IP1|ARV1|ATP2B4|B9D2|CCDC23|CDK16', regex=True)]

#selected_genes = [
#    "APOB", "BEAN1", "CCDC23", "COX14", "COX6A2", "DHFR", "DKC1", "EIF2AK1", "FITM2", "FZR1",
    #"HIKESHI", "HIP1R", "KIAA1715", "LYRM7", "NOL3", "NPHP1", "OBFC1", "PAX9", "POU4F1", "RAD50",
    #"REPS1", "RFC4", "RNF220", "SARS", "SARS2", "SELRC1", "SLC39A4", "SLC6A19", "SLC9A1", "STXBP2",
#    "THG1L", "TTC21B", "UROC1", "VWA3B"
#]

df = df[df['symbol'].isin(selected_genes)]

if "symbol" not in df.columns:
    raise ValueError("ERROR: The TSV file must contain a 'symbol' column.")

# Function to query OpenAI API and classify response
def query_ataxia_flag(gene_symbol):
    # prompt = f"Are variants in {gene_symbol} associated with neurological symptoms? Respond with 'Yes' if there is evidence of an association, 'No' if no evidence"
    # prompt = f"Are variants in {gene_symbol} associated with neurological disorders? Respond with 'Yes' if there is evidence of an association, 'No' if no evidence"
    # prompt = f"We are testing to determine if you can identify if a gene is involved in any way to neurological disorders or disease with neurological symptoms or brain development.  Are variants in {gene_symbol} associated with this? Respond with 'Yes' if there is evidence of an association, 'No' if no evidence"
    prompt = f"Are mutations in the gene {gene_symbol} associated with neurological symptoms or neurological disorders? Respond with 'Yes' if there is evidence of an association, 'No' if no evidence"
    # gpt-4o vs gpt-4 which is Turbo.  gpt-4o give 6 whereas gpt-4 gives 5
    try:
        response = client.chat.completions.create(
            # test with gpt-4 and 03-mini
            # model="gpt-4",  # Adjust model if needed
            # model="o3-mini",
            messages=[{"role": "system", "content": "You are a genetic expert providing concise responses."},
                      {"role": "user", "content": prompt}],
            # max_tokens=20,
            # max_completion_tokens=20,
            #temperature=0.0
            # temperature=0.3
            # temperature=0.7
        )

        output = response.choices[0].message.content.strip().lower()
        # print output
        # print(f"Gene: {gene_symbol}, Output: {output}")
        if "yes" in output:
            return 1  # API flagged it as associated with ataxia
        elif "no" in output:
            return 0  # API did not associate with ataxia
        else:
            return 2  # API is unsure

    except Exception as e:
        print(f"ERROR querying {gene_symbol}: {e}")
        return 2

df["API_Flag"] = df["symbol"].apply(query_ataxia_flag)

output_file = "data/processed/ataxia_api_results3.csv"
df.to_csv(output_file, index=False)

print(f"\n API flagging complete! Results saved to {output_file}\n")
print(df[["symbol", "API_Flag"]].head(100))  # Print first 10 results
