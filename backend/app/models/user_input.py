from pydantic import BaseModel, Field
from typing import List, Optional

class UserInput(BaseModel):
    """Model for user input data."""
    account_description: Optional[str] = Field(
        None, 
        description="Optional description of the social media account, including tone, niche, and goals"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "account_description": "I run a vegan food blog focusing on quick meals. My audience is primarily 25-35 year old professionals. I want to grow my follower count and drive traffic to my recipe website."
            }
        } 