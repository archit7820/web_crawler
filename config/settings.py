from pydantic_settings import BaseSettings 
from pathlib import Path

class Settings(BaseSettings):
    PROJECT_NAME: str = "Web Crawler API"
    DEBUG: bool = True
    OUTPUT_DIR: Path = Path(__file__).resolve().parent.parent / "output"
    USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ..."
    REQUEST_TIMEOUT: int = 30
    MAX_CONCURRENT_REQUESTS: int = 10
    
    class Config:
        env_file = ".env"

def get_settings():
    return Settings()
