# TODO: назвать этот файл согласно тому что он делает (пока что очень общее название)

"""
TODO:
Эндпоинт с запросом в чатгпт:

1/ Сериализация/десериализация объектов Chat в json, сами json-ы храним в redis chat_id: json с expiration time

2/ Появляется отношение instagram_user_id-chat one-to-one: в redis храним instagram_id: chat_id

3/ Сама логика работы эндпоинта:

Достаем “сырой“ Chat (или собираем новый),
который хранит в себе только описание аккаунта от llm (все взаимодействие с клиентами),
этот чат обновляется с expiration time или позднее

“сырой“ чат дополняем тем, что хотим получить от llm сейчас, например
chat = LoadStoredChat(id)
chat.prompt("Появилось новое сообщение/комментарий {текст сообщения/комментария}")
OpenAIClient().prompt(chat, "Сгенерируй ответ на {личное сообщение/комментарий} {текст комментария или сообщения}") -> текст ответа, который эндпоинт вернет
так как никакой новой информации не появляется, объект chat освобождается, контекст обновляется потом eventually

Отдаем текст  с предыдущего шага
"""
from app.infrastructure.openai_client import Chat, OpenAIClient
from app.infrastructure.redis_client import redis_client


class ChatGptService:
    def __init__(self):
        self.redis = redis_client
        self.openai_client = OpenAIClient()
        self.context_expiration_time = 100000   # todo: move to env file
        self.chat_gpt_prompt = "Появилось новое сообщение/комментарий"  # todo: naming? move to .env?

    @staticmethod
    def _instagram_id_naming_strategy(inst_id: str) -> str:
        return "inst:" + inst_id

    # todo: как пишем ручку если это по идее webhook'и должны дергать? какая то безопасность при запросе?
    # todo: пока обрабатывает только текст
    def handle_incoming_interaction(self, receiver_inst_id: str, incoming_content: str) -> str:
        """
        Обработать новое сообщение или комментарий и предложить вариант ответа на него.
        """
        receiver_inst_id_redis = self._instagram_id_naming_strategy(receiver_inst_id)
        chat = self.redis.get(receiver_inst_id_redis)
        if chat is None:
            # todo: получить описание чата от ваниного метода
            receiver_account_description = "Самый интересный и смешной аккаунт во всем Instagram"

            chat = Chat()
            chat.preset_with_instruction(receiver_account_description)

            ok = self.redis.setex(receiver_inst_id_redis, self.context_expiration_time, chat.serialize())
            if not ok:
                raise RuntimeError(f"Failure when store context for user {receiver_inst_id} in Redis")

        # todo: зачем добавлять incoming_content и в propmpt чата и в запрос ответа от openai_client
        chat.add_prompt(self.chat_gpt_prompt + incoming_content)
        return self.openai_client.prompt(chat, f"Сгенерируй ответ на личное сообщение/комментарий {incoming_content}")


if __name__ == "__main__":
    # chat = Chat().preset_with_instruction("Ты помощник").add_prompt("Привет")
    # json_string = chat.serialize()
    #
    # print(json_string)
    #
    # new_chat = Chat.deserialize(json_string)
    # print(new_chat.contexts)

    chat_gpt_service = ChatGptService()
    print(chat_gpt_service.handle_incoming_interaction("100500", "Some new comment"))

    redis_client.setex("test_key", 1000, "test_value")
    print(redis_client.get("test_key"))
