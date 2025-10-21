"""Configuration management for the RPG API."""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Configuration
    api_secret_key: str = "dev-secret-key-change-in-production"
    api_title: str = "Bastards Blood RPG API"
    api_version: str = "1.0.0"
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    
    # CORS Configuration
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    # Data paths
    data_path: str = "./bastards-blood/data"
    schemas_path: str = "./bastards-blood/schemas"
    
    # LLM Configuration (optional)
    llm_api_key: str = ""
    llm_model: str = "gpt-4"
    llm_endpoint: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
