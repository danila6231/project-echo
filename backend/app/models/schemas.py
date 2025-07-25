from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional


class ContentIdea(BaseModel):
    """Model for a single content idea."""
    content_type: str = Field(..., description="Type of the content (e.g. post, story, reel, etc.)")
    title: str = Field(..., description="Brief title/theme of the content idea")
    theme: str = Field(..., description="Brief description of the post theme or concept")
    caption_draft: str = Field(..., description="Suggested caption for the post")
    hashtag_suggestions: List[str] = Field(..., description="List of relevant hashtags")
    reason: str = Field(..., description="Reason why this idea is relevant to the account and might be engaging for the audience")

class ContentIdeasResponse(BaseModel):
    """Model for the complete output response."""
    account_summary: str = Field(..., description="Brief summary of the account based on analysis")
    content_ideas: List[ContentIdea] = Field(..., description="List of suggested content ideas")
    token: str = Field(..., description="Session token for retrieving this response again")

class ShortLivedTokenDto(BaseModel):
    access_token: str = Field()
    user_id: int = Field(..., description="User ID")
    permissions: List[str] = Field(..., description="List of permissions to grant access to this token")

class LongLivedTokenDto(BaseModel):
    access_token: str = Field()
    token_type: str = Field()
    expires_in: int = Field()

class Post(BaseModel):
    id: str = Field()

class Comment(BaseModel):
    id: str = Field()

class Cursors(BaseModel):
    before: Optional[str] = Field(default=None)
    after: Optional[str] = Field(default=None)

class Paging(BaseModel):
    cursors: Cursors = Field()
    next: Optional[str] = Field(default=None)

class PostsDto(BaseModel):
    data: List[Post] = Field()
    paging: Paging = Field()

class CommentsDto(BaseModel):
    data: List[Comment] = Field()
    paging: Paging = Field()

class UserInfoDto(BaseModel):
    user_id: str = Field()
    username: str = Field()
    id: str = Field()

class Conversation(BaseModel):
    id: str = Field()
    updated_time: datetime = Field()

class ConversationsDto(BaseModel):
    data: Optional[List[Conversation]] = Field(default=None)

class InstUser(BaseModel):
    username: str = Field()
    id: str = Field()

class MessageReceivers(BaseModel):
    data: List[InstUser] = Field()

class MessageInfo(BaseModel):
    id: str = Field()
    created_time: datetime = Field()
    from_user: Optional[InstUser] = Field(default=None, alias="from")
    to_user: Optional[MessageReceivers] = Field(default=None, alias="to")
    message: Optional[str] = Field(description="Message content", default=None)

class MessageMetainfo(BaseModel):
    id: str = Field()
    created_time: datetime = Field()
    is_unsupported: bool = Field()

class Messages(BaseModel):
    data: List[MessageMetainfo] = Field()
    paging: Paging = Field()

class DialogDto(BaseModel):
    messages: Messages = Field()
    id: str = Field()

class SendingMessageResponseDto(BaseModel):
    recipient_id: str = Field()
    message_id: str = Field()
