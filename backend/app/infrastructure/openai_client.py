import json
import openai
import base64
from pathlib import Path
from typing import List, Dict
from app.core.config.main_config import settings

from pydantic import BaseModel, Field, ValidationError


def _encode_image(image_path: str) -> str:
    """Encodes image to base64 string."""
    image_bytes = Path(image_path).read_bytes()
    return base64.b64encode(image_bytes).decode("utf-8")


class ChatJSON(BaseModel):
    # context: List[Dict[str, str]] = Field(..., title="Context")
    context: List = Field(..., title="Context")


class Chat:
    def __init__(self, context = None):
        self._context: List[Dict[str, str]] = [] if context is None else context

    # TODO: staticmethod? builder?
    def preset_with_instruction(self, preset: str):
        content = [{"type": "input_text", "text": preset}]
        self._context.append({'role': 'system', 'content': content})
        return self

    def preset_images(self, image_list: List[str] = None):
        content = []
        for image in image_list:
            content.append({"type": "input_image", "image_url": image})
        self._context.append({'role': 'user', 'content': content})
        return self
    
    def add_prompt(self, prompt: str = None, image_url: str = None, role: str = 'user'):
        if prompt is not None:
            self._context.append({'role': role, 'content': prompt})
        if image_url is not None:
            self._context.append({'role': role, "content": [
                {
                    "type": "input_image",
                    "image_url": image_url,
                },
            ]})
        return self

    def add_response(self, response: str):
        self._context.append({'role': 'assistant', 'content': response})

    @property
    def contexts(self):
        return self._context

    def serialize(self) -> str:
        chat_json = ChatJSON(context=self._context)
        return chat_json.model_dump_json()

    @staticmethod
    def deserialize(context: str) -> "Chat":
        try:
            data = json.loads(context)
        except json.JSONDecodeError as e:
            raise ValueError(f"Некорректный JSON: {e}")

        try:
            chat_data = ChatJSON(**data)
        except ValidationError as e:
            raise ValueError(f"Структура данных не соответствует ожидаемой модели: {e}")

        return Chat(chat_data.context)


class OpenAIClient:
    def __init__(self, model=settings.LLM_MODEL):
        self.model = model
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        self.chats: Dict[str, Chat] = {}

    def prompt(self, chat: Chat, text: str = None, image_url: str = None) -> str:
        if text:
            chat.add_prompt(text, image_url)
        # print(chat.contexts)
        response = self.client.responses.create(
            model=self.model,
            input=chat.contexts
        )
        response = response.output_text.strip()
        chat.add_response(response)
        return response
