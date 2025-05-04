import json
import redis
from typing import Any, Dict, Optional, Union

from app.core.config import settings

class RedisClient:
    def __init__(self):
        """Initialize Redis connection using configuration settings."""
        if settings.REDIS_URL:
            self.redis = redis.from_url(settings.REDIS_URL)
        else:
            redis_ssl = False
            if settings.REDIS_HOST != "localhost":
                redis_ssl = True
            self.redis = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD,
                decode_responses=True,
                ssl=redis_ssl
            )
    
    def get(self, key: str) -> Optional[str]:
        """Get a value from Redis."""
        return self.redis.get(key)
    
    def set(self, key: str, value: str, expiry: Optional[int] = None) -> bool:
        """Set a value in Redis with optional expiry time."""
        return self.redis.set(key, value, ex=expiry or settings.TOKEN_EXPIRY)
    
    def delete(self, key: str) -> bool:
        """Delete a key from Redis."""
        return bool(self.redis.delete(key))
    
    def store_json(self, key: str, data: Dict[str, Any], expiry: Optional[int] = None) -> bool:
        """Store JSON data in Redis."""
        return self.set(key, json.dumps(data), expiry)
    
    def get_json(self, key: str) -> Optional[Dict[str, Any]]:
        """Get JSON data from Redis."""
        data = self.get(key)
        if data:
            return json.loads(data)
        return None
    
    def check_connection(self) -> bool:
        """Test if Redis connection is working."""
        try:
            return bool(self.redis.ping())
        except Exception:
            return False

# Create a global Redis client instance
redis_client = RedisClient() 