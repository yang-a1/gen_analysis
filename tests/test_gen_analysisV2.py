import pytest
import os
from gen_analysis_module.gen_analysisV2 import generate_elaboration
# from gen_analysisV2 import generate_elaboration
# from gen_analysis_module.config import TEST_DIR, TEST_DATA_DIR, RAW_DATA_DIR, INTERIM_DATA_DIR




# # Get all .tsv files from RAW_DATA_DIR
# tsv_files = [file for file in os.listdir(TEST_DATA_DIR) if file.endswith(".tsv")]
#
# # Process each .tsv file
# for file in tsv_files:
#     file_path = os.path.join(RAW_DATA_DIR, file)
#     # Process the file
#



def test_generate_elaboration():
    prompt = "This is a test prompt."
    elaboration = generate_elaboration(prompt)
    assert isinstance(elaboration, str)
    assert len(elaboration) > 0


