#!/bin/bash

conda activate gen_analysis

# Get the current directory
current_dir=$(pwd)

# Define the target directory
target_dir="gen_analysis/contrib"

# List files in the ../data/raw directory
echo "Files in ../data/raw:"
ls ../data/raw

# Ask the user if they want to continue
read -p "Do you want to continue? (yes/no): " user_input

if [[ "$user_input" != "yes" ]]; then
    echo "Operation aborted by the user."
    exit 1
fi

# Check if the current directory matches the target directory
if [[ "$current_dir" == *"$target_dir" ]]; then
    # Run the Python script
    python ../gen_analysis_module/gen_analysis.py > ../data/processed/temp_output.md
    sed -i 's/Gene: \[/# Gene: \[/g' ../data/processed/temp_output.md
    pandoc ../data/processed/temp_output.md -o ../data/processed/temp_output.docx
else
    echo "You are not in the gen_analysis/contrib directory."
fi


