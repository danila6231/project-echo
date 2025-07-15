import requests
import os
from app.core.config.main_config import settings

CLIENT_SECRET = settings.INSTAGRAM_CLIENT_SECRET
CLIENT_ID = settings.INSTAGRAM_CLIENT_ID

class InstagramAPI:
    def __init__(self, redirect_url: str):
        self.redirect_url = redirect_url
        self.access_token = None
        self.long_lived_token = None

    def authorize(self, client_id: str, client_secret: str, code: str):
        """
        Exchange the authorization code for a short-lived access token.
        """
        url = "https://api.instagram.com/oauth/access_token"
        payload = {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "authorization_code",
            "redirect_uri": self.redirect_url,
            "code": code
        }
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            self.access_token = response.json().get("access_token")
        return response.json()

    def long_lived(self, client_secret: str):
        """
        Exchange the short-lived token for a long-lived access token.
        """
        url = "https://graph.instagram.com/access_token"
        params = {
            "grant_type": "ig_exchange_token",
            "client_secret": client_secret,
            "access_token": self.access_token
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

    def posts(self):
        """
        Get all posts for the user.
        """
        url = f"https://graph.instagram.com/v23.0/me/media"
        params = {"access_token": self.long_lived_token}
        response = requests.get(url, params=params)
        return response.json()

    def comments(self, post_id: str):
        """
        Get all comments for a specific post.
        """
        url = f"https://graph.facebook.com/v16.0/{post_id}/comments"
        params = {"access_token": self.long_lived_token}
        response = requests.get(url, params=params)
        return response.json()