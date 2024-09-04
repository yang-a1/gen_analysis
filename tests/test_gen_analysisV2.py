import pytest
from gen_analysis_module.gen_analysisV2 import generate_elaboration

def test_generate_elaboration():
    prompt = "This is a test prompt."
    elaboration = generate_elaboration(prompt)
    assert isinstance(elaboration, str)
    assert len(elaboration) > 0