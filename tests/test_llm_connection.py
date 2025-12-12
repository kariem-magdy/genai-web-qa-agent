import pytest
from app.core.llm import get_llm
import os

def test_llm_instantiation():
    if not os.getenv("GOOGLE_API_KEY"):
        pytest.skip("No API Key provided")
    try:
        llm = get_llm()
        assert llm is not None
    except ValueError:
        pytest.fail("API Key missing")