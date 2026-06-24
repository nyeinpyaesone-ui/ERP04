"""Configuration management for AI ERP backend."""
import os
from typing import Optional

class Settings:
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "AI ERP System"
    APP_VERSION: str = "3.3.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://erp_user:erp_password@localhost:5432/erp_db"
    )
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "erp_user")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "erp_password")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "erp_db")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", "5432"))
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev_secret_key_change_in_production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    
    # Data paths
    DATA_DIR: str = os.getenv("DATA_DIR", "data")
    TOWNSHIPS_FILE: str = os.path.join(DATA_DIR, "townships.json")
    TAX_RATES_FILE: str = os.path.join(DATA_DIR, "tax_rates.json")
    
    def __init__(self):
        self._validate_settings()
    
    def _validate_settings(self):
        """Validate critical settings."""
        if self.DEBUG:
            print(f"⚠️  Running in DEBUG mode - DO NOT use in production!")
        
        if self.SECRET_KEY == "dev_secret_key_change_in_production":
            print(f"⚠️  Using default SECRET_KEY - Change immediately in production!")

# Global settings instance
settings = Settings()
