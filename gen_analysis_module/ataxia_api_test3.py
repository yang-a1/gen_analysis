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

if not all([OPENAI_API_KEY, API_VERSION, OPENAI_ORG, OPENAI_ENDPOINT]):
    raise ValueError("ERROR: One or more OpenAI credentials are missing. Check your .env file.")

client = AzureOpenAI(
    api_key=OPENAI_API_KEY,
    api_version=API_VERSION,
    azure_endpoint=OPENAI_ENDPOINT,
    organization=OPENAI_ORG
)

file_path = "data/raw/Chicago_Ataxia_Exome_Gene_List_2.tsv"

if not os.path.exists(file_path):
    raise FileNotFoundError(f"ERROR: File '{file_path}' not found. Ensure the path is correct.")

df = pd.read_csv(file_path, sep="\t")

if "symbol" not in df.columns:
    raise ValueError("ERROR: The TSV file must contain a 'symbol' column.")

# Function to query OpenAI API and classify response
def query_ataxia_flag(gene_symbol):
    prompt = f"Is the gene {gene_symbol} associated with ataxia? Respond with 'Yes' if there is a known association, 'No' if not, and 'Uncertain' if evidence is unclear."

    try:
        response = client.chat.completions.create(
            model="gpt-4",  # Adjust model if needed
            messages=[{"role": "system", "content": "You are a genetic expert providing concise responses."},
                      {"role": "user", "content": prompt}],
            max_tokens=20,
            temperature=0.3
        )

        output = response.choices[0].message.content.strip().lower()

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

output_file = "data/processed/ataxia_api_results.csv"
df.to_csv(output_file, index=False)

print(f"\n API flagging complete! Results saved to {output_file}\n")
print(df[["symbol", "API_Flag"]].head(10))  # Print first 10 results
