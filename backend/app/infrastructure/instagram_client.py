import json

import requests
from app.core.config.main_config import settings
from app.models.schemas import PostsDto, ShortLivedTokenDto, LongLivedTokenDto, CommentsDto, UserInfoDto, \
    ConversationsDto, DialogDto, MessageInfo, SendingMessageResponseDto

# TODO: предлагаю переименовать с CLIENT_<что-то> -> APP_<что-то>; как я понимаю это данные именно нашего приложения
CLIENT_SECRET = settings.INSTAGRAM_CLIENT_SECRET
CLIENT_ID = settings.INSTAGRAM_CLIENT_ID
APP_URI = settings.INSTAGRAM_REDIRECT_URI


class InstagramApiClient:
    def __init__(self):
        self.redirect_url = APP_URI
        self.short_lived_token = None
        self.long_lived_token = None
        self.user_id = None

    def get_short_lived_token(self, code: str) -> ShortLivedTokenDto:
        """
        Exchange the authorization code for a short-lived access token.
        """
        url = "https://api.instagram.com/oauth/access_token"
        client_id = CLIENT_ID
        client_secret = CLIENT_SECRET
        payload = {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "authorization_code",
            "redirect_uri": self.redirect_url,
            "code": code
        }
        response = requests.post(url, data=payload)
        mapped_response = None
        if response.status_code == 200:
            mapped_response = ShortLivedTokenDto.model_validate(response.json())
            self.short_lived_token = mapped_response.access_token
            self.user_id = mapped_response.user_id
        return mapped_response

    def get_long_lived_token(self) -> LongLivedTokenDto:
        """
        Exchange the short-lived token for a long-lived access token.
        """
        url = "https://graph.instagram.com/access_token"
        client_secret = CLIENT_SECRET
        params = {
            "grant_type": "ig_exchange_token",
            "client_secret": client_secret,
            "access_token": self.short_lived_token
        }
        response = requests.get(url, params=params)
        mapped_response = None
        if response.status_code == 200:
            mapped_response = LongLivedTokenDto.model_validate(response.json())
            self.long_lived_token = mapped_response.access_token
        return mapped_response

    def get_conversations(self) -> ConversationsDto:
        """
        List all conversations or conversations with a specific user.
        """
        url = f"https://graph.instagram.com/v23.0/me/conversations"
        params = {"access_token": self.long_lived_token, "platform": "instagram"}
        response = requests.get(url, params=params)
        return ConversationsDto.model_validate(response.json())

    def get_conversations_with_user(self, user_id: str) -> ConversationsDto:
        """
        List all conversations or conversations with a specific user.
        """
        url = f"https://graph.instagram.com/v23.0/me/conversations"
        params = {
            "access_token": self.long_lived_token,
            "user_id": user_id
        }
        response = requests.get(url, params=params)
        return ConversationsDto.model_validate(response.json())

    def get_messages_in_conversation(self, conversation_id: str) -> DialogDto:
        """
        Get all messages in a specific conversation.
        """
        url = f"https://graph.instagram.com/v23.0/{conversation_id}"
        params = {"access_token": self.long_lived_token, "fields": "messages"}
        response = requests.get(url, params=params)
        return DialogDto.model_validate(response.json())

    def get_message_info(self, message_id: str) -> MessageInfo:
        """
        Get information (id, created_time, from, to, message) about a specific message.

        WARNING (from doc):
        Note: Queries to the /<CONVERSATION_ID> endpoint will return all message IDs in a conversation.
        However, you can only get details about the 20 most recent messages in the conversation.
        If you query a message that is older than the last 20, you will see an error that the message has been deleted.
        """
        url = f"https://graph.instagram.com/v23.0/{message_id}"
        params = {
            "access_token": self.long_lived_token,
            "fields": "id,created_time,from,to,message",
        }
        response = requests.get(url, params=params)
        return MessageInfo.model_validate(response.json())

    def send_text_message(self, sender_id: str, recipient_id: str, text: str) -> SendingMessageResponseDto:
        """
        Send a message to a user.
        """
        url = f"https://graph.instagram.com/v23.0/{sender_id}/messages"
        headers = {
            'Authorization': f'Bearer {self.long_lived_token}',
            'Content-Type': 'application/json'
        }
        payload = {
            'recipient': {
                'id': recipient_id
            },
            'message': {
                'text': text
            }
        }
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        return SendingMessageResponseDto.model_validate(response.json())

    # TODO
    def send_private_reply(self, recipient: str, text: str):
        """
        Send a private reply to a comment.
        """
        url = f"https://graph.instagram.com/v16.0/{recipient}/private_replies"
        payload = {
            "message": text,
            "access_token": self.long_lived_token
        }
        response = requests.post(url, data=payload)
        return response.json()

    def get_posts(self) -> PostsDto:
        """
        Get all posts for the user.
        """
        # TODO: pagination here
        url = f"https://graph.instagram.com/v23.0/me/media"
        params = {"access_token": self.long_lived_token}
        response = requests.get(url, params=params)
        response_json = response.json()
        return PostsDto.model_validate(response_json)

    def get_comments(self, post_id: str) -> CommentsDto:
        """
        Get all comments for a specific post.
        """
        url = f"https://graph.instagram.com/v23.0/{post_id}/comments"
        params = {"access_token": self.long_lived_token}
        response = requests.get(url, params=params)
        return CommentsDto.model_validate(response.json())

    def get_me_info(self) -> UserInfoDto:
        """
        Получить инфу о пользаке инсты от апишки инсты
        """
        url = f"https://graph.instagram.com/v16.0/me"
        params = {"fields": "user_id,username", "access_token": self.long_lived_token}
        response = requests.get(url, params=params)
        return UserInfoDto.model_validate(response.json())

    # TODO: dto
    def post_details(self, post_id: str):
        """
        Get detailed information about a specific post.
        """
        url = f"https://graph.instagram.com/v23.0/{post_id}"
        params = {"fields": "id,caption,media_type,media_url,thumbnail_url,permalink,timestamp", "access_token": self.long_lived_token}
        response = requests.get(url, params=params)
        return response.json()

    # TODO: dto
    def comment_details(self, comment_id: str):
        """
        Get detailed information about a specific comment.
        """
        url = f"https://graph.instagram.com/v23.0/{comment_id}"
        params = {"fields": "id,text,username,timestamp", "access_token": self.long_lived_token}
        response = requests.get(url, params=params)
        return response.json()

    # TODO: dto
    def private_dialog_details(self, dialog_id: str):
        """
        Get detailed information about a specific private dialog.
        """
        url = f"https://graph.instagram.com/v16.0/{dialog_id}/messages"
        params = {"fields": "id,message,from,to,timestamp", "access_token": self.long_lived_token}
        response = requests.get(url, params=params)
        return response.json()