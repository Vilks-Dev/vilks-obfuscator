import os
import tempfile
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_ENV: str = "production"
    RATE_LIMIT_UPLOADS: str = "10/minute"
    RATE_LIMIT_REQUESTS: str = "50/minute"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024
    ALLOWED_EXTENSIONS: List[str] = [".py", ".zip", ".tar.gz"]
    SANDBOX_DOCKER_IMAGE: str = "python-obfuscator-sandbox:latest"
    SANDBOX_TIMEOUT: int = 10
    API_TIMEOUT: int = 15
    UPLOAD_DIR: str = os.path.join(tempfile.gettempdir(), "obfuscator_uploads")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
