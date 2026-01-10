"""
Configuration management
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Application settings"""

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://admin:changeme@localhost:5432/polymarket_tracker"
    )
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
    DB_NAME: str = os.getenv("DB_NAME", "polymarket_tracker")
    DB_USER: str = os.getenv("DB_USER", "admin")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "changeme")

    # API
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))

    # Polymarket APIs
    POLYMARKET_DATA_API: str = os.getenv(
        "POLYMARKET_DATA_API",
        "https://data-api.polymarket.com"
    )
    POLYMARKET_GAMMA_API: str = os.getenv(
        "POLYMARKET_GAMMA_API",
        "https://gamma-api.polymarket.com"
    )
    POLYMARKET_CLOB_API: str = os.getenv(
        "POLYMARKET_CLOB_API",
        "https://clob.polymarket.com"
    )

    # Collection settings
    COLLECTION_INTERVAL_SECONDS: int = int(os.getenv("COLLECTION_INTERVAL_SECONDS", "300"))
    TRADES_FETCH_LIMIT: int = int(os.getenv("TRADES_FETCH_LIMIT", "1000"))

    # Detection settings
    SUSPICIOUS_THRESHOLD: int = int(os.getenv("SUSPICIOUS_THRESHOLD", "20"))
    FRESH_WALLET_DAYS: int = int(os.getenv("FRESH_WALLET_DAYS", "30"))
    FRESH_WALLET_MAX_TXS: int = int(os.getenv("FRESH_WALLET_MAX_TXS", "20"))
    FRESH_WALLET_MAX_POSITION: int = int(os.getenv("FRESH_WALLET_MAX_POSITION", "10000"))

    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
