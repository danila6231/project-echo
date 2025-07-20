from pydantic import BaseModel, Field
from datetime import datetime
from typing import List


# TODO: удалить вместе со всем связанным кодом
class ContentIdea(BaseModel):
    """Model for a single content idea."""
    content_type: str = Field(..., description="Type of the content (e.g. post, story, reel, etc.)")
    title: str = Field(..., description="Brief title/theme of the content idea")
    theme: str = Field(..., description="Brief description of the post theme or concept")
    caption_draft: str = Field(..., description="Suggested caption for the post")
    hashtag_suggestions: List[str] = Field(..., description="List of relevant hashtags")
    reason: str = Field(..., description="Reason why this idea is relevant to the account and might be engaging for the audience")

# TODO: удалить вместе со всем связанным кодом
class ContentIdeasResponse(BaseModel):
    """Model for the complete output response."""
    account_summary: str = Field(..., description="Brief summary of the account based on analysis")
    content_ideas: List[ContentIdea] = Field(..., description="List of suggested content ideas")
    token: str = Field(..., description="Session token for retrieving this response again")

class ShortLivedTokenDto(BaseModel):
    # todo: узнать у вани че за токен возвращает метод 'authorize'
    access_token: str = Field()
    user_id: int = Field(..., description="User ID")
    permissions: List[str] = Field(..., description="List of permissions to grant access to this token")

class LongLivedTokenDto(BaseModel):
    access_token: str = Field()
    token_type: str = Field()
    expires_in: int = Field()

class Post(BaseModel):
    id: str = Field()

class Cursors(BaseModel):
    before: str = Field()
    after: str = Field()

class Paging(BaseModel):
    cursors: Cursors = Field()

class PostsDto(BaseModel):
    data: List[Post] = Field()
    paging: Paging = Field()

"""
Message from Direct.
"""
class Message(BaseModel):
    id: str = Field(..., description="Message id")
    sender_id: str = Field(...)
    text: str = Field(...)
    timestamp: datetime = Field(...)

"""
Comment for post.
"""
class Comment:
    id: str
    post_id: str
    sender_id: str
    text: str
    timestamp: datetime

class ConversationContext:
    thread_id: str
    messages: List[Message]

class CommentContext:
    post_id: str
    comments: List[Comment]

# TODO: как будто нужна еще сущность user - Ваня говорил что по ней определяется кому отправлять ответ (?)
