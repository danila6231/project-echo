from app.infrastructure.openai_client import Chat, OpenAIClient
from app.infrastructure.redis_client import redis_client
from app.services.instagram_snapshot import describe_instagram_account, LONG_LIVED_TOKEN
from app.core.config.main_config import settings


class ChatGptService:
    def __init__(self):
        self.redis = redis_client
        self.openai_client = OpenAIClient()
        self.context_expiration_time = settings.CONTEXT_EXPIRATION_TIME
        self.chat_gpt_prompt = "Появилось новое сообщение/комментарий"  # todo: naming? move to .env?

    @staticmethod
    def instagram_id_naming_strategy(inst_id: str) -> str:
        return "inst:" + str(inst_id)

    # todo: пока обрабатывает только текст
    def handle_incoming_interaction(self, receiver_inst_id: str, receiver_long_lived_token: str, incoming_content: str = None) -> str:
        """
        Обработать новое сообщение или комментарий и предложить вариант ответа на него.
        """

        receiver_inst_id_redis = self.instagram_id_naming_strategy(receiver_inst_id)
        receiver_chat_bytes = self.redis.get(receiver_inst_id_redis)
        if receiver_chat_bytes is None:
            receiver_account_description = describe_instagram_account(receiver_long_lived_token)

            receiver_chat = Chat().preset_with_instruction(receiver_account_description)

            ok = self.redis.setex(receiver_inst_id_redis, self.context_expiration_time, receiver_chat.serialize())
            if not ok:
                raise RuntimeError(f"Failure when store context for user {receiver_inst_id} in Redis")
        else:
            receiver_chat = Chat().deserialize(receiver_chat_bytes.decode("utf-8"))
        return self.openai_client.prompt(receiver_chat, f"Сгенерируй ответ на личное сообщение/комментарий {incoming_content}")