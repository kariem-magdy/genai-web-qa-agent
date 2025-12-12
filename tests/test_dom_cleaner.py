import pytest
from app.engine.dom_cleaner import DOMCleaner

def test_script_removal():
    html = "<html><script>alert('x')</script><body><h1>Hi</h1></body></html>"
    clean = DOMCleaner.clean_dom(html)
    assert "<script>" not in clean
    assert "alert" not in clean
    assert "<h1>Hi</h1>" in clean

def test_attribute_filtering():
    html = '<input type="text" onclick="bad()" data-test="login-input" style="color:red">'
    clean = DOMCleaner.clean_dom(html)
    assert 'onclick' not in clean
    assert 'style' not in clean
    assert 'data-test="login-input"' in clean