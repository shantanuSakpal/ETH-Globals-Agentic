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
    JWT_SECRET: str = os.getenv("JWT_SECRET", "your-jwt-secret-key-here")
    
    # Database
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
    
    # Web3 Settings
    WEB3_PROVIDER_URI: str = os.getenv("WEB3_PROVIDER_URI", "http://localhost:8545")
    CHAIN_ID: int = int(os.getenv("CHAIN_ID", "1"))
    
    # Morpho Protocol Settings
    MORPHO_CONTRACT_ADDRESS: str = os.getenv("MORPHO_CONTRACT_ADDRESS", "")
    
    # Price Feed Settings
    PRICE_FEED_API_KEY: Optional[str] = os.getenv("PRICE_FEED_API_KEY")
    
    # CDP Settings
    CDP_API_KEY_NAME: str = os.getenv("CDP_API_KEY_NAME", "")
    CDP_API_KEY_PRIVATE_KEY: str = os.getenv("CDP_API_KEY_PRIVATE_KEY", "")
    NETWORK_ID: str = os.getenv("NETWORK_ID", "base-sepolia")
    
    # LLM Settings
    LLM_MODEL: str = os.environ.get("LLM_MODEL", "gpt-4o")

    #DATABASE SETTINGS
    MONGODB_URL: str = os.getenv("MONGODB_URL")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME")
    
    # Add WebSocket settings
    WS_HEARTBEAT_INTERVAL: int = 30  # seconds
    WS_CONNECTION_TIMEOUT: int = 60  # seconds
    
    # New field
    VAULT_FACTORY_ADDRESS: str = os.getenv("VAULT_FACTORY_ADDRESS")
    DEPLOYER_PRIVATE_KEY: str = os.getenv("DEPLOYER_PRIVATE_KEY")
   

    class Config:
        env_file = ".env"
        case_sensitive = True
        env_file_encoding = 'utf-8'
        #extra = "forbid"

@lru_cache()
def get_settings() -> Settings:
    return Settings() 