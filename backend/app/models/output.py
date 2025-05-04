from pydantic import BaseModel, Field
from typing import List, Optional

class ContentIdea(BaseModel):
    """Model for a single content idea."""
    content_type: str = Field(..., description="Type of the content (e.g. post, story, reel, etc.)")
    title: str = Field(..., description="Brief title/theme of the content idea")
    theme: str = Field(..., description="Brief description of the post theme or concept")
    caption_draft: str = Field(..., description="Suggested caption for the post")
    hashtag_suggestions: List[str] = Field(..., description="List of relevant hashtags")
    reason: str = Field(..., description="Reason why this idea is relevant to the account and might be engaging for the audience")

class OutputResponse(BaseModel):
    """Model for the complete output response."""
    account_summary: str = Field(..., description="Brief summary of the account based on analysis")
    content_ideas: List[ContentIdea] = Field(..., description="List of suggested content ideas")
    token: str = Field(..., description="Session token for retrieving this response again") 