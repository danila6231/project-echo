import os
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseModel):
    # API configs
    API_V1_PREFIX: str = "/api/v1"
    
    # Development settings
    SKIP_LOGIN: bool = os.getenv("SKIP_LOGIN", "False").lower() == "true"  # Set to True to bypass auth checks
    TEST_USER_USERNAME: str = os.getenv("TEST_USER_USERNAME", "michael")
    TEST_USER_ACCOUNT_TYPE: str = os.getenv("TEST_USER_ACCOUNT_TYPE", "business")
    TEST_USER_ID: str = os.getenv("TEST_USER_ID", "test_user_123")
    TEST_USER_TOKEN: str = os.getenv("TEST_USER_TOKEN", "test_token")
    
    # OpenAI settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
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
    
    # Instagram App Settings
    INSTAGRAM_CLIENT_ID: str = os.getenv("INSTAGRAM_CLIENT_ID", "")
    INSTAGRAM_CLIENT_SECRET: str = os.getenv("INSTAGRAM_CLIENT_SECRET", "")
    INSTAGRAM_REDIRECT_URI: str = os.getenv("INSTAGRAM_REDIRECT_URI", "https://google.com/")
    
    # Session Settings
    SESSION_EXPIRY: int = int(os.getenv("SESSION_EXPIRY", "86400"))  # 24 hours in seconds
    COOKIE_SECURE: bool = os.getenv("COOKIE_SECURE", "False").lower() == "true"  # Set to True in production
    
    # Frontend URL
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")

# Create global settings object
settings = Settings() 