import secrets
import json
from typing import Optional, Dict, Any
from app.infrastructure.redis_client import redis_client
from app.core.config.main_config import settings

class SessionManager:
    def __init__(self):
        self.redis = redis_client
        self.session_prefix = "session:"
        self.session_expiry = settings.SESSION_EXPIRY
    
    def create_session(self, user_data: Dict[str, Any]) -> str:
        """Create a new session for a user."""
        session_id = secrets.token_urlsafe(32)
        session_key = f"{self.session_prefix}{session_id}"
        
        # Store session data in Redis
        self.redis.setex(
            session_key,
            self.session_expiry,
            json.dumps(user_data)
        )
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve session data by session ID."""
        session_key = f"{self.session_prefix}{session_id}"
        session_data = self.redis.get(session_key)
        
        if not session_data:
            return None
        
        return json.loads(session_data)
    
    def update_session(self, session_id: str, user_data: Dict[str, Any]) -> bool:
        """Update existing session data."""
        session_key = f"{self.session_prefix}{session_id}"
        
        # Check if session exists
        if not self.redis.exists(session_key):
            return False
        
        # Update session data
        self.redis.setex(
            session_key,
            self.session_expiry,
            json.dumps(user_data)
        )
        
        return True
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        session_key = f"{self.session_prefix}{session_id}"
        return bool(self.redis.delete(session_key))
    
    def extend_session(self, session_id: str) -> bool:
        """Extend session expiry time."""
        session_key = f"{self.session_prefix}{session_id}"
        return bool(self.redis.expire(session_key, self.session_expiry))

# Create global session manager instance
session_manager = SessionManager() 