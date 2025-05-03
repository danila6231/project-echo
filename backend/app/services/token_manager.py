import secrets
import uuid
from typing import Dict, Optional

from app.redis.redis_client import redis_client
from app.core.config import settings

class TokenManager:
    """Manages session tokens for user requests and responses."""
    
    @staticmethod
    def generate_token() -> str:
        """Generate a new unique token."""
        return str(uuid.uuid4())
    
    @staticmethod
    def store_response(token: str, response_data: Dict) -> bool:
        """Store LLM response in Redis, keyed by token."""
        return redis_client.store_json(token, response_data, settings.TOKEN_EXPIRY)
    
    @staticmethod
    def get_response(token: str) -> Optional[Dict]:
        """Retrieve a stored response by token."""
        return redis_client.get_json(token)
    
    @staticmethod
    def delete_token(token: str) -> bool:
        """Delete a token and its associated data."""
        return redis_client.delete(token)

# Create global token manager
token_manager = TokenManager() 