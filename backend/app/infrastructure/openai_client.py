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
    context: List[Dict[str, str]] = Field(..., title="Context")


class Chat:
    def __init__(self, context = None):
        self._context: List[Dict[str, str]] = [] if context is None else context

    # TODO: staticmethod? builder?
    def preset_with_instruction(self, preset: str):
        self._context.append({'role': 'system', 'content': preset})
        return self

    def add_prompt(self, prompt: str, image_url: str = None):
        if image_url:
            self._context.append({'role': 'user', "content": [
                {"type": "input_text", "text": prompt},
                {
                    "type": "input_image",
                    "image_url": image_url,
                },
            ]})
        else:
            self._context.append({'role': 'user', 'content': prompt})
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
        self.client = openai.OpenAI(api_key="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")
        self.chats: Dict[str, Chat] = {}

    def prompt(self, chat: Chat, text: str = None, image_url: str = None) -> str:
        if text:
            chat.add_prompt(text, image_url)

        response = self.client.responses.create(
            model=self.model,
            input=chat.contexts
        )
        response = response.output_text.strip()
        chat.add_response(response)
        return response
