import pytest
import sys
import os
import ast
import re
import base64

# Add parent directory to path to import sandbox.engine.obfuscator
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sandbox.engine.obfuscator import Obfuscator

def extract_inner_payload(wrapped_code: str) -> str:
    match = re.search(r'base64\.b64decode\(b"([^"]+)"\)', wrapped_code)
    if not match:
        raise ValueError("Could not find base64 payload in wrapper")
    encoded_payload = match.group(1)
    return base64.b64decode(encoded_payload).decode("utf-8")

def test_basic_obfuscation():
    code = """
def add(a, b):
    \"\"\"This is a docstring.\"\"\"
    result = a + b
    return result
"""
    obfuscator = Obfuscator(code, "basic")
    obfuscated = obfuscator.obfuscate()
    
    assert "add add(" not in obfuscated
    
    inner_payload = extract_inner_payload(obfuscated)
    assert "This is a docstring" not in inner_payload
    assert "add" not in inner_payload or "_0x" in inner_payload
    assert "result" not in inner_payload or "_0x" in inner_payload

    # Ensure output wrapper is valid Python
    parsed = ast.parse(obfuscated)
    assert isinstance(parsed, ast.Module)

def test_standard_obfuscation():
    code = """
def get_secret():
    secret_str = "flag{secure_string}"
    return secret_str
"""
    obfuscator = Obfuscator(code, "standard")
    obfuscated = obfuscator.obfuscate()
    
    assert "flag{secure_string}" not in obfuscated
    
    inner_payload = extract_inner_payload(obfuscated)
    assert "flag{secure_string}" not in inner_payload
    assert "_0xdec" in inner_payload
    
    parsed = ast.parse(obfuscated)
    assert isinstance(parsed, ast.Module)

def test_hardcore_obfuscation():
    code = """
def main():
    val = 42
    print(val)
"""
    obfuscator = Obfuscator(code, "hardcore")
    obfuscated = obfuscator.obfuscate()
    
    assert "# Protected by Vilks" in obfuscated
    assert "# INTEGRITY: " in obfuscated
    
    inner_payload = extract_inner_payload(obfuscated)
    assert "_0xverify" in inner_payload
    assert "_0xcheck_dbg" in inner_payload
    
    parsed = ast.parse(obfuscated)
    assert isinstance(parsed, ast.Module)

def test_syntax_validation():
    invalid_code = """
def main(
    print("broken code")
"""
    with pytest.raises(ValueError):
        obfuscator = Obfuscator(invalid_code, "basic")
        obfuscator.obfuscate()
