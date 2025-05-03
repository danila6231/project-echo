import os
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseModel):
    # API configs
    API_V1_PREFIX: str = "/api/v1"
    
    # OpenAI settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o")
    
    # Redis settings
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "")
    REDIS_URL: str = os.getenv("REDIS_URL", "")
    
    # Token expiry (in seconds, default 1 hour)
    TOKEN_EXPIRY: int = int(os.getenv("TOKEN_EXPIRY", "3600"))
    
    # CORS
    CORS_ORIGINS: list = ["*"]  # For development; restrict in production

# Create global settings object
settings = Settings() 