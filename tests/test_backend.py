import sys
import os
import pytest
import re
import base64
from fastapi.testclient import TestClient

# Add parent directory to path to import backend
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Configure test environment
os.environ["APP_ENV"] = "development"

from backend.app.main import app

client = TestClient(app)

def extract_inner_payload(wrapped_code: str) -> str:
    match = re.search(r'base64\.b64decode\(b"([^"]+)"\)', wrapped_code)
    if not match:
        raise ValueError("Could not find base64 payload in wrapper")
    encoded_payload = match.group(1)
    return base64.b64decode(encoded_payload).decode("utf-8")

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "sandbox_ready" in data

def test_obfuscate_text_success():
    payload = {
        "code": "def hello():\n    print('hello')\n",
        "level": "basic"
    }
    response = client.post("/obfuscate-text", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "obfuscated_code" in data
    
    # Assert wrapper comments
    assert "# Protected by Vilks" in data["obfuscated_code"]
    
    # Assert inner code renaming
    inner = extract_inner_payload(data["obfuscated_code"])
    assert "_0x" in inner

def test_obfuscate_text_invalid_syntax():
    payload = {
        "code": "def hello(\n    print('hello')\n",
        "level": "basic"
    }
    response = client.post("/obfuscate-text", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert "Invalid Python syntax" in data["detail"]

def test_obfuscate_file_py():
    file_content = b"def test():\n    return 1\n"
    files = {"file": ("test.py", file_content, "text/plain")}
    data = {"level": "basic"}
    
    response = client.post("/obfuscate", files=files, data=data)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/octet-stream"
    
    wrapped_code = response.content.decode("utf-8")
    assert "# Protected by Vilks" in wrapped_code
    
    inner = extract_inner_payload(wrapped_code)
    assert "_0x" in inner

def test_obfuscate_file_invalid_extension():
    file_content = b"some content"
    files = {"file": ("test.txt", file_content, "text/plain")}
    data = {"level": "basic"}
    
    response = client.post("/obfuscate", files=files, data=data)
    assert response.status_code == 400
    data = response.json()
    assert "Extension not allowed" in data["detail"]

def test_obfuscate_file_too_large():
    # 11MB file
    file_content = b"0" * (11 * 1024 * 1024)
    files = {"file": ("large.py", file_content, "text/plain")}
    data = {"level": "basic"}
    
    response = client.post("/obfuscate", files=files, data=data)
    assert response.status_code == 413
    data = response.json()
    assert "exceeds 10 MB" in data["detail"]
