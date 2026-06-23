import re
import os
import ast
from fastapi import HTTPException, status
from backend.app.config import settings

def validate_filename(filename: str) -> str:
    if not filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is missing"
        )
    
    clean_name = os.path.basename(filename)
    if clean_name != filename or ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid filename: path traversal characters detected"
        )
    
    _, ext = os.path.splitext(clean_name)
    if ext.lower() not in settings.ALLOWED_EXTENSIONS and not clean_name.endswith(".tar.gz"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Extension not allowed. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    
    if not re.match(r'^[\w\-. ]+$', clean_name.replace(".tar.gz", "").replace(".zip", "").replace(".py", "")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename contains forbidden special characters"
        )
    
    return clean_name

def validate_python_code(code: str) -> None:
    try:
        ast.parse(code)
    except SyntaxError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid Python syntax: {str(e)}"
        )
