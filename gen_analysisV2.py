import csv
import os
from collections import defaultdict
import openai 
from dotenv import load_dotenv, find_dotenv 

# Load the .env file and get the OpenAI API Key from .env file
_ = load_dotenv(find_dotenv())
openai.api_key = os.environ.get('OPENAI_API_KEY')

def get_elaboration(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=300, 
        temperature=0.7,  
        top_p=1.0, 
        frequency_penalty=0.0,
        presence_penalty=0.0
    )
    return response.choices[0].message['content'].strip()

def create_prompts(gene):
    mouse_phenotype_prompt = (
        f"Describe in detail the mouse phenotype associated with mutations in the gene {gene}. "
        "Focus on observed phenotypes in mice homozygous for an ENU-induced mutation, including cardiac hypertrophy, aorta hypoplasia, stenosis, and bicuspid aortic valve. "
        "Explain how these phenotypes manifest in mice, the potential underlying mechanisms, and any relevant studies or findings that highlight these effects. "
        "Provide insights into how these phenotypes might be indicative of the gene's role in cardiovascular development and pathology."
    )

    omim_prompt = (
        f"Provide a detailed overview of the gene {gene} as listed in OMIM and GeneCards. "
        "Elaborate on the diseases associated with {gene}, including Endocardial Fibroelastosis and Subvalvular Aortic Stenosis. "
        "Describe the gene’s function and its role in these diseases. Include information on the gene's expression, protein products, and any known mutations or variants linked to these conditions. "
        "Explain how mutations in {gene} might lead to the development of these diseases and discuss any significant findings or research related to this gene."
    )

    return mouse_phenotype_prompt, omim_prompt

def process_tsv_file(filename):
    variants = {}
    
    with open(filename, mode='r', newline='') as file:
        reader = csv.DictReader(file, delimiter='\t')
        
        for row in reader:
            symbol = row['symbol'].strip("[]").strip("'")
            variant_class = row['variant_class'].strip()
            gnomad_af = row['gnomadg_af'].strip("[]").strip("'") if row['gnomadg_af'].strip() else 'nan'
            max_af = row['max_af'].strip()
            
            if symbol not in variants:
                variants[symbol] = []
            
            variants[symbol].append({
                'type': variant_class,
                'frequency_gnomad': gnomad_af,
                'frequency_max': max_af,
                'effect': 'unknown'  # Placeholder since effect information is not available
            })
    
    return variants

def format_output(variants):
    for gene, data in variants.items():
        print(f"{gene}")
        print("Types of variants with frequencies:")
        
        for idx, variant in enumerate(data):
            print(f"{idx + 1}. {variant['type']}: ")
            print(f"   a. Gnomade allele frequency: {variant['frequency_gnomad']}")
            print(f"   b. Max allele frequency: {variant['frequency_max']}")
            print(f"   c. Amino acid change: ND")
            print(f"   d. Effect of amino acid change: {variant['effect']}")
            print(f"   e. polyphen/sift: ND/ND")
        print("\n")

def main():
    tsv_file = '20240701_example_file_v2.xlsx - Sheet1.tsv'
    variants = process_tsv_file(tsv_file)

    for gene in variants:
        mouse_phenotype_prompt, omim_prompt = create_prompts(gene)
                
        mouse_phenotype_description = get_elaboration(mouse_phenotype_prompt)
        omim_description = get_elaboration(omim_prompt)
        
        print(mouse_phenotype_description)
        print(f"\nOMIM Description for {gene}:")
        print(omim_description)
        print("\n")

    format_output(variants)

if __name__ == "__main__":
    main()
