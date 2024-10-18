import pytest
import os
from gen_analysis_module.gen_analysis import generate_elaboration, get_files_in_folder
# from gen_analysis import generate_elaboration
from gen_analysis_module.config import TEST_DIR, TEST_DATA_DIR, RAW_DATA_DIR, INTERIM_DATA_DIR





# Get all .tsv files from RAW_DATA_DIR
tsv_files = [file for file in os.listdir(TEST_DATA_DIR) if file.endswith(".tsv")]
# Process each .tsv file
for file in tsv_files:
    file_path = os.path.join(RAW_DATA_DIR, file)
    print(file_path)
    if os.path.exists(file_path):
        print("File exists.")
    else:
        print("File does not exist.")

# test get_files_in_folder
def test_get_files_in_folder():
    file_paths = get_files_in_folder(TEST_DATA_DIR)
    assert isinstance(file_paths, list)
    assert len(file_paths) > 0
    for file_path in file_paths:
        assert os.path.exists(file_path)


def test_generate_elaboration():
    prompt = "This is a test prompt."
    elaboration = generate_elaboration(prompt)
    assert isinstance(elaboration, str)
    assert len(elaboration) > 0


