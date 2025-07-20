import requests
from app.core.config.main_config import settings
from app.models.schemas import PostsDto

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

    def get_short_lived_token(self, code: str):
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
        if response.status_code == 200:
            self.short_lived_token = response.json().get("access_token")
            # todo: тут возвращается важная инфа про пользака - его id
            self.user_id = response.json().get("user_id")
        return response.json()

    def get_long_lived_token(self):
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
        if response.status_code == 200:
            self.long_lived_token = response.json().get("access_token")
        return response.json()

    def conversations(self, user_id: str):
        """
        List all conversations or conversations with a specific user.
        """
        url = f"https://graph.facebook.com/v16.0/{user_id}/conversations"
        params = {"access_token": self.long_lived_token}
        response = requests.get(url, params=params)
        return response.json()

    def dialog(self, conversation_id: str):
        """
        Get all messages in a specific conversation.
        """
        url = f"https://graph.facebook.com/v16.0/{conversation_id}/messages"
        params = {"access_token": self.long_lived_token}
        response = requests.get(url, params=params)
        return response.json()

    def message(self, message_id: str):
        """
        Get information about a specific message.
        """
        url = f"https://graph.facebook.com/v16.0/{message_id}"
        params = {"access_token": self.long_lived_token}
        response = requests.get(url, params=params)
        return response.json()

    def send_message(self, recipient: str, text: str):
        """
        Send a message to a user.
        """
        url = f"https://graph.facebook.com/v16.0/{recipient}/messages"
        payload = {
            "message": text,
            "access_token": self.long_lived_token
        }
        response = requests.post(url, data=payload)
        return response.json()

    def send_private_reply(self, recipient: str, text: str):
        """
        Send a private reply to a comment.
        """
        url = f"https://graph.facebook.com/v16.0/{recipient}/private_replies"
        payload = {
            "message": text,
            "access_token": self.long_lived_token
        }
        response = requests.post(url, data=payload)
        return response.json()

    def posts(self) -> PostsDto:
        """
        Get all posts for the user.
        """
        url = f"https://graph.instagram.com/v23.0/me/media"
        params = {"access_token": self.long_lived_token}
        response = requests.get(url, params=params)
        response_json = response.json()
        return PostsDto.model_validate(response_json)

    def comments(self, post_id: str):
        """
        Get all comments for a specific post.
        """
        url = f"https://graph.facebook.com/v16.0/{post_id}/comments"
        params = {"access_token": self.long_lived_token}
        response = requests.get(url, params=params)
        return response.json()

    def get_user_info(self):
        """
        Получить инфу о пользаке инсты от апишки инсты
        """
        url = f"https://graph.facebook.com/v16.0/me"
        params = {"fields": "user_id,username", "access_token": self.long_lived_token}
        response = requests.get(url, params=params)
        return response.json()