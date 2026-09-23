from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "DEFEND-X API"
    ENVIRONMENT: str = "local"
    # Provide a default SQLite DB for testing/development if URL is empty
    DATABASE_URL: str = "sqlite:///./test.db"
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USERNAME: str = "neo4j"
    NEO4J_PASSWORD: str = "password"
    AUTH_SECRET: str = "supersecret_default_do_not_use_in_prod"
    FRONTEND_URL: str = "http://localhost:3000"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen2.5:1.5b"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
