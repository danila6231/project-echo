import openai
import base64
from pathlib import Path
from typing import List, Dict


def _encode_image(image_path: str) -> str:
    """Encodes image to base64 string."""
    image_bytes = Path(image_path).read_bytes()
    return base64.b64encode(image_bytes).decode("utf-8")


class Chat:
    def __init__(self):
        self._context: List[Dict[str, str]] = []

    def preset_with_instruction(self, instruction: str):
        self._context.append({'role': 'system', 'content': instruction})
        return self

    def prompt(self, prompt: str, image_path: str = None):
        if image_path:
            base64_image = _encode_image(image_path)
            self._context.append({'role': 'user', "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    },
                },
            ]})
        else:
            self._context.append({'role': 'user', 'content': prompt})
        return self

    def set_response(self, response: str):
        self._context.append({'role': 'assistant', 'content': response})

    @property
    def contexts(self):
        return self._context


class OpenAIClient:
    def __init__(self, model="gpt-4-vision-preview"):
        self.model = model
        self.chats: Dict[str, Chat] = {}

    def prompt(self, chat: Chat, text: str, image_path: str = None) -> str:
        chat.prompt(text, image_path)

        response = openai.ChatCompletion.create(
            model=self.model,
            messages=chat,
            max_tokens=1000,
        )
        response = response['choices'][0]['message']['content']
        chat.set_response(response)
        return response.strip()
