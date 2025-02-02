from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Application Settings
    APP_NAME: str = "Helenus AI"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
    
    # Web3 Settings
    WEB3_PROVIDER_URI: str = os.getenv("WEB3_PROVIDER_URI", "http://localhost:8545")
    CHAIN_ID: int = int(os.getenv("CHAIN_ID", "1"))
    
    # Morpho Protocol Settings
    MORPHO_CONTRACT_ADDRESS: str = os.getenv("MORPHO_CONTRACT_ADDRESS", "")
    
    # Price Feed Settings
    PRICE_FEED_API_KEY: Optional[str] = os.getenv("PRICE_FEED_API_KEY")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings() 