# Genome Analysis

[![CCDS-Project Template](https://img.shields.io/badge/CCDS-Project%20template-328F97?logo=cookiecutter)](https://cookiecutter-data-science.drivendata.org/)

## Gene Analysis Module User Guide

Welcome to the Gene Analysis Module! This tool is specifically designed to streamline the analysis of gene variant data, allowing you to generate insightful elaborations and produce cleanly formatted reports in both Markdown and PDF formats.

Given the vast number of genes, manually searching for information on each one related to your area of interest can be incredibly time-consuming. This is where our tool offers a significant advantage. By leveraging the ChatGPT API, you can expedite your research process by submitting questions related to specific genes involved in variant analysis. The tool queries the API to determine if a particular gene could be associated with the type of genetic variant analysis you are conducting, saving you invaluable time and effort.

This guide will walk you through the steps to use the Gene Analysis Module effectively, enabling you to make the most of its capabilities for your research endeavors.

## Table of Contents
- [Overview](#overview)
- [Installation](#installation)
- [Configuration](#configuration)
- [Using the Tool](#using-the-tool)
- [Prepare Your Data](#prepare-your-data)
- [Generate Reports](#generate-reports)
- [Output Formats](#output-formats)
- [Prompts and Elaboration Generation](#prompts-and-elaboration-generation)
- [Handling Errors and Rate Limiting](#handling-errors-and-rate-limiting)
- [Additional Notes](#additional-notes)
- [Directory Structure](#directory-structure)
- [License](#license)

## Overview
The Gene Analysis Module is a Python-based tool that processes gene variant data in TSV (Tab-Separated Values) format. The module extracts relevant information such as gene symbols, allele frequencies, and variant consequences, then formats it for easy viewing. By leveraging the OpenAI API, the tool generates dynamic elaborations for gene symbols based on user-defined prompts. These elaborations provide deeper insights into gene variants, making the data more useful for researchers.

The module outputs the processed data in Markdown and PDF formats, making it easy to integrate into reports or documentation.

## Installation
To get started with the Gene Analysis Module, follow the installation steps below:

### Access the ARC Environment

SSH into the ARC (Advanced Research Computing) system at the University of Michigan:

```bash
ssh greatlakes.arc-ts.umich.edu
```
### Load and Activate the Conda Environment


Load the Conda module:


```bash
module load python/anaconda
```
Activate the Conda environment that contains the necessary dependencies:
bash:


```bash
conda activate gene-analysis-env
```
If the environment is not already created, you can create it by running:
bash


```bash
conda create -n gene-analysis-env python=3.8 pandas numpy openai python-dotenv
conda activate gene-analysis-env
```
### Clone the Repository


Clone this repository:
```bash
git clone https://github.com/yang-a1/gen-analysis-module.git
```
### Set Up the Environment Configuration


Create a .env file in the root directory of the project, and add the following configuration variables:
```ini
OPENAI_API_KEY=your-api-key
model=gpt-35-turbo
API_VERSION=2024-06-01
prompts_json_file="prompts.json"
MAX_TOKENS_VALUE=150
TEMPERATURE_VALUE=0.7
```
Make sure to replace the placeholders with your actual OpenAI API key, organization value, and any required URLs for accessing Azure OpenAI. The above example can be found in gen_analysis.env.example.

## Prepare Your Data
Place your TSV files (gene variant data) in the appropriate folder (`RAW_DATA_DIR`). The tool will process these files and generate detailed Markdown reports.  
Ensure that your dataset has the required columns, including `chromosome`, `position`, `allele`, `symbol`, `impact`, etc. You can configure which columns to extract by modifying the `process_file` function.

## Configuration

### Environment Variables
The module uses environment variables defined in the `.env` file. Here’s an explanation of each variable:

- **OPENAI_API_KEY**: Required for interacting with OpenAI's API. You can obtain it by signing up on OpenAI's platform.
- **model**: Specifies the OpenAI model to use for generating elaborations. The default model is `gpt-35-turbo`, but you can use other models depending on your needs.
- **API_VERSION**: The version of the OpenAI API you're using. This is set to `2024-06-01` in the example.
- **prompts_json_file**: Path to the JSON file containing predefined prompts. The prompts are used to generate detailed elaborations on gene symbols.
- **MAX_TOKENS_VALUE**: The maximum number of tokens (words/characters) that OpenAI will generate in response to each prompt.
- **TEMPERATURE_VALUE**: Controls the creativity of the responses. A higher value (e.g., `0.7`) results in more creative responses, while a lower value (e.g., `0.3`) generates more predictable responses.

### Prompts JSON File
The `prompts.json` file should be structured as a dictionary, where each key is a prompt template, and the value is the corresponding prompt. For example:

```json
{
    "mouse_prompt": "Provide a professional, detailed description of mouse phenotypes associated with {gene_symbol}.",
    "omim_prompt": "Provide a professional, detailed description of diseases associated with {gene_symbol} as found in OMIM/GeneCards."
}
```

In the above example, the `{gene_symbol}` placeholder will be replaced with the actual gene symbol when generating elaborations.

## Using the Tool

### Prepare Your Data

To process your data, make sure your variant information is stored in a TSV file with the following columns (among others):

- **chromosome**: Chromosomal location.
- **position**: Position on the chromosome.
- **allele**: Genetic variant (e.g., A/G).
- **symbol**: Gene symbol.
- **gnomadg_af**: Allele frequency from the gnomAD database.
- **max_af**: Maximum allele frequency across populations.
- **impact**: Impact of the variant (e.g., benign, pathogenic).
- **hgvsg**: The variant's HGVS string.
- **clinical significance**: The clinical significance of the variant.

Ensure your data is placed in the directory specified by the `RAW_DATA_DIR` environment variable.

### Generate Reports

Once your data is ready and the environment is configured, run the following command to process your files and generate the reports:

```bash
python gen_analysis.py
```
This command will:
- Load the prompts from the `prompts.json` file.
- Process all TSV files in the `RAW_DATA_DIR` directory.
- Generate elaborations for each gene symbol.
- Output the results in Markdown format.
- Convert the Markdown files to PDF format using the custom CSS specified in `CSS_CONTENT`.

## Output Formats

### Markdown Output

Each processed file will generate a `.md` file with the variant data formatted in Markdown. The file will include:

- A header with the filename.
- Detailed variant information, including the elaborations generated for each gene symbol.
- Specific variant details like allele frequencies, amino acid changes, and other relevant annotations.

### PDF Output

The `.md` files are converted to PDF format using a custom CSS file. This provides a clean and professional layout for presenting the data.

## Prompts and Elaboration Generation

The module generates detailed elaborations for each gene symbol using OpenAI’s GPT-3 model. These elaborations provide insights into the gene’s function, potential variant impacts, and other relevant details. The elaborations are generated dynamically based on predefined prompts, which can be customized to suit your needs.

For example, if you have a gene symbol "BRCA1", the prompt might ask the model to generate a detailed description of BRCA1's function and its known variants.

## Handling Errors and Rate Limiting

### Errors

The tool includes error handling to manage issues such as:

- Missing or empty input files.
- Incorrect file formats.
- API errors.

### Rate Limiting

If the tool encounters OpenAI’s rate limit (when too many requests are made in a short period), it will automatically pause for 60 seconds and retry the request. This ensures that the process can continue without interruption.

## Additional Notes

- **Customizing Prompts**: You can easily adjust the prompts in the `prompts.json` file to modify the elaborations generated by the OpenAI model.
- **Large Data Files**: If your TSV files contain more than 1000 lines, the tool will reject them to ensure that processing remains manageable. You can adjust the line limit by changing the `max_lines` parameter in the script.

## Directory Structure

### `contrib/`
This folder contains utility scripts and additional resources to aid users in executing analyses.


- **`20241004_quickrun_gen_analysisV2.sh`**: A bash script that activates a conda environment and lists files in the raw data directory. It prompts the user for confirmation before running the `gen_analysis.py` script, which processes genetic data and generates reports in Markdown and DOCX formats.


- **`pandoc.sh`**: A simple script example for converting Markdown files to DOCX using Pandoc.


- **`rm_request_open_terminal.sh`**: A script to submit an interactive job to a SLURM scheduler, providing access to a terminal for executing commands.


### `gen_analysis_module/`
This module includes the core functionality for data processing and analysis.


- **`config.py`**: Configures project directories and loads environment variables. Sets paths for raw, processed, and external data.


- **`dataset.py`**: Contains a command-line interface for processing datasets, with customizable input and output paths.


- **`features.py`**: Similar to `dataset.py`, this script generates features from processed datasets and allows for path customization.


- **`gen_analysis.py`**: The main analysis script that reads TSV files, processes genetic variant information, and generates elaborated descriptions using the OpenAI API.


- **`plots.py`**: A placeholder for future plotting functionalities, designed to generate visual representations of the processed data.


### `tests/`
This directory includes test cases to ensure the functionality of the project.


- **`test_gen_analysis.py`**: Uses `pytest` to validate the existence of TSV files in the test data directory and tests the core functions for getting file paths and generating elaboration from prompts.


### `data/`
Contains various test cases in the form of TSV files used for validating the functionality of the scripts. Notable files include:


- **`empty.tsv`**
- **`extracol.tsv`**
- **`header.tsv`**
- **`malformed.tsv`**
- **`missingcol.tsv`**
- **`test_file_1.tsv`**
- **`test_file_2.tsv`**


### Usage
To run the analysis, follow these steps:
1. Navigate to the `contrib` directory.
2. Execute the `20241004_quickrun_gen_analysisV2.sh` script.
3. Confirm the continuation when prompted.
4. The analysis will be executed, generating outputs in the specified formats.


### SLURM Job Management
The project includes guidelines for submitting jobs to SLURM, with a focus on managing job numbers and ensuring the correct environment is activated for execution.


### Additional Notes
- Ensure that the necessary environment variables for the OpenAI API are set in the `.env` file.
- For any issues related to the SLURM job environment, refer to the provided commands and troubleshooting steps.

### Project Organization

```
├── LICENSE            <- Open-source license if one is chosen
├── Makefile           <- Makefile with convenience commands like `make data` or `make train`
├── README.md          <- The top-level README for developers using this project.
├── data
│   ├── external       <- Data from third party sources.
│   ├── interim        <- Intermediate data that has been transformed.
│   ├── processed      <- The final, canonical data sets for modeling.
│   └── raw            <- The original, immutable data dump.
│
├── docs               <- A default mkdocs project; see mkdocs.org for details
│
├── models             <- Trained and serialized models, model predictions, or model summaries
│
├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
│                         the creator's initials, and a short `-` delimited description, e.g.
│                         `1.0-jqp-initial-data-exploration`.
│
├── pyproject.toml     <- Project configuration file with package metadata for gen_analysis_module
│                         and configuration for tools like black
│
├── references         <- Data dictionaries, manuals, and all other explanatory materials.
│
├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
│   └── figures        <- Generated graphics and figures to be used in reporting
│
├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
│                         generated with `pip freeze > requirements.txt`
│
├── setup.cfg          <- Configuration file for flake8
│
└── gen_analysis_module                <- Source code for use in this project.
    │
    ├── __init__.py    <- Makes gen_analysis_module a Python module
    │
    ├── data           <- Scripts to download or generate data
    │   └── make_dataset.py
    │
    ├── features       <- Scripts to turn raw data into features for modeling
    │   └── build_features.py
    │
    ├── models         <- Scripts to train models and then use trained models to make
    │   │                 predictions
    │   ├── predict_model.py
    │   └── train_model.py
    │
    └── visualization  <- Scripts to create exploratory and results oriented visualizations
        └── visualize.py
```

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Contact

If you have any questions or would like to get in touch, feel free to reach out to us via email:  
- delpropo@med.umich.edu  
- amyyan@umich.edu  
