"""
Application configuration settings using Pydantic BaseSettings.
Loads environment variables from .env file.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application configuration settings loaded from environment variables.
    
    Attributes:
        APP_NAME: Application display name.
        APP_VERSION: Application version string.
        MONGO_URI: MongoDB connection URI.
        DATABASE_NAME: MongoDB database name.
        SEARCH_COLLECTION: MongoDB collection name for search documents.
        CACHE_EXPIRY_SECONDS: Cache validity duration in seconds.
        SERPER_API_KEY: API key for Serper service.
        SERPER_URL: Base URL for Serper API.
        OLLAMA_URL: Base URL for Ollama service.
        REQUEST_TIMEOUT: Timeout for external API requests in seconds.
    """
    APP_NAME: str
    APP_VERSION: str
    MONGO_URI: str
    DATABASE_NAME: str
    SEARCH_COLLECTION: str
    CACHE_EXPIRY_SECONDS: int = 60
    SERPER_API_KEY: str
    SERPER_URL: str
    OLLAMA_URL: str
    REQUEST_TIMEOUT: int = 120

    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


def get_settings() -> Settings:
    """Returns a Settings instance loaded from environment configuration."""
    return Settings()


settings = get_settings()
