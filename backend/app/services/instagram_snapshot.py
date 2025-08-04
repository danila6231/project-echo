from typing import List, NamedTuple

import requests
import json

from app.infrastructure.instagram_client import InstagramApiClient
from app.infrastructure.openai_client import Chat, OpenAIClient
from app.infrastructure.redis_client import RedisClient
from app.models.schemas import CommentInfoDto


def post_to_str(post_json) -> str:
    post_text = post_json['caption']
    image_included = post_json['media_type'] == 'IMAGE'
    prompt_text = f'Instagram post with text: "{post_text}"'
    if image_included:
        prompt_text += f" and related image: {post_json['media_url']}"
    # print(f"prompt post: {prompt_text}")
    return prompt_text


def comment_to_str(comment_json) -> str:
    comment_text = comment_json['text']
    prompt_text = f'Comment from user: "{comment_text}"'
    # print(f"prompt comment: {prompt_text}")
    return prompt_text


def dialogs_to_str(dialogs_json, me_id: str) -> str:
    prompt_text = "Here is user private dialog:\n"
    for dialog in dialogs_json:
        for message in dialog['data']:
            if message['from']['id'] == me_id:
                # why message['to'] is list?
                prompt_text += f"{message['message']} from user to {message['to']['data'][0]['username']}\n"
            else:
                prompt_text += f"{message['message']} from {message['from']['username']} to user\n"
    # print(f"prompt dialog: {prompt_text}")
    return prompt_text


def describe_instagram_account(token: str) -> str:
    """
    Description consists of:
    1) posts data
    2) replies to comments
    3) private dialogs
    """
    # TODO: передавать клиент вместо токена
    client = InstagramApiClient().with_long_lived_token(token)

    # Fetch posts data
    posts_data = client.get_posts()
    user_info = client.get_me_info()

    # Start providing context
    gpt_client = OpenAIClient()
    chat = Chat()

    content_pieces = []
    post_images = []
    # Fetch detailed posts data
    for post in posts_data.data:
        post_content = client.post_details(post.id)
        prompt_text = post_to_str(post_content)
        if post_content['media_type'] == 'IMAGE':
            post_images.append(post_content['media_url'])
        content_pieces.append(prompt_text)
        
        content_pieces.append("Comments for the post:")
        comments = client.get_comments(post.id)
        for comment in comments.data:
            comment_detailed = client.comment_details(comment.id)
            prompt_text = comment_to_str(comment_detailed)
            content_pieces.append(prompt_text)

        

    # Fetch private dialogs
    private_dialogs = client.get_conversations()

    # Fetch detailed private dialogs
    detailed_private_dialogs = [client.private_dialog_details(dialog.id) for dialog in private_dialogs.data]

    # print(f"dialogs: {detailed_private_dialogs}")
    prompt_text = dialogs_to_str(detailed_private_dialogs, user_info.user_id)
    content_pieces.append(prompt_text)

    content_pieces = "\n".join(content_pieces)
    
    chat.preset_with_instruction(f"""
You are given a concatenated string containing past Instagram posts, comments, captions, and private messages from a single account:
<START_OF_CONTENT>
{content_pieces}
Post images are attached as files in the first user message.
<END_OF_CONTENT>
Your task is to extract the identity of this account. You will use this summary to guide your responses to future comments or DMs in a tone and style consistent with the account.

Please be sure to extract the following:

1. Account Topic  
What is the main theme or subject of this Instagram account?  
(e.g., fitness, baking, digital art, small business marketing tips, etc.)

2. Audience Description  
What type of audience is this account targeting?  
(e.g., amateur bakers, Gen Z creatives, small business owners, etc.)

3. Writing Style & Tone  
What is the tone and writing style used in captions and replies?  
Include examples of quirks, emojis, catchphrases, humor, or specific expressions.  
(e.g., friendly and casual with lots of 🍞 emojis and bread puns)

4. Typical Topics & Themes  
List a few recurring content categories or subjects discussed.

5. Notable Values or Opinions  
Does the account express any opinions, beliefs, or consistent values?  
(e.g., promoting sustainability, encouraging beginners, etc.)

6. Call-to-Actions / Business Goals (if any)  
Does the account try to sell something, promote a brand, grow engagement, or offer any services?

7. Voice Emulation Summary  
Brief understanding on how to replicate the account’s voice in future replies.  
(e.g., “When replying to messages, use playful tone, include emojis, ask friendly questions, never sound too formal.”)


In the queries you’ll be asked to write replies to a provided comment or message that was sent to the account.

General recommendations:
1) Never mention that you are AI, your responses will NEVER include warnings, disclaimers, etc. such as, but not limited to, "As an Al", "As a large language mode" "As an artificial intelligence, I don't have feelings or emotions" The user already knows you are an LLM. Just skip to the answer.
2) ONLY INCLUDE THE EXACTS SUGGESTED RESPONSE in your output. Do not include any other text.
3) Never make any promises or guarantees that are not explicitly stated in the description of the account.
    """)

    chat.preset_images(post_images)
    return chat


#TODO
#todo: как будто хуева что эти функции оказались тут, проеб layout'а нашего проекта
#todo: можно выдавать по 5 новых id-шников на вызов функции
class CommentInfo(NamedTuple):
    text: str
    new_flg: bool


def get_new_comments_id(api_client: InstagramApiClient, redis_client: RedisClient) -> List[CommentInfo]:
    """Retrieve not handled Instagram comments."""
    all_comments = []
    posts_data = api_client.get_posts()
    for post in posts_data.data:
        for comment in api_client.get_comments(post.id).data:
            all_comments.append(comment.id)

    redis_comments_key = "comments_" + api_client.get_me_info().user_id

    last_retrieved_comments_str = redis_client.get(redis_comments_key)

    # update anyway
    redis_client.set(redis_comments_key, json.dumps(all_comments))

    new_comments = set()
    if last_retrieved_comments_str:
        last_retrieved_comments = json.loads(last_retrieved_comments_str)

        new_comments = set(last_retrieved_comments).symmetric_difference(set(all_comments))

    return [CommentInfo(text=comment_id, new_flg=(comment_id in new_comments)) for comment_id in all_comments]


class MessageView(NamedTuple):
    text: str
    new_flg: bool


def get_new_messages_id(api_client: InstagramApiClient, redis_client: RedisClient) -> List[MessageView]:
    all_messages = []
    new_messages = []
    # Fetch private dialogs
    private_dialogs = api_client.get_conversations()

    me_id = api_client.get_me_info().user_id

    redis_message_key = "messages_" + me_id

    # Fetch detailed private dialogs
    detailed_private_dialogs = [api_client.private_dialog_details(dialog.id) for dialog in private_dialogs.data]

    for dialog in detailed_private_dialogs:
        for message in dialog['data']:
            if message['from']['id'] != me_id:
                all_messages.append(message['id'])

    last_retrieved_messages_str = redis_client.get(redis_message_key)

    # update anyway
    redis_client.set(redis_message_key, json.dumps(all_messages))

    if last_retrieved_messages_str:
        last_retrieved_messages = json.loads(last_retrieved_messages_str)

        new_messages = list(set(last_retrieved_messages).symmetric_difference(set(all_messages)))

    return [MessageView(text=message_id, new_flg=(message_id in new_messages)) for message_id in all_messages]


#TODO
def get_comment_info_by_id(instagram_client: InstagramApiClient, comment_id: str) -> CommentInfoDto:
    comment_detailed = instagram_client.comment_details(comment_id)
    # print(comment_detailed)
    post_of_comment = instagram_client.post_details(comment_detailed["media"]["id"])
    # print(post_of_comment)

    data = {
        "id": comment_id,
        "text": comment_detailed["text"],
        "username": comment_detailed["from"]["username"],
        "timestamp": comment_detailed["timestamp"],
        "post_id": comment_detailed["media"]["id"],
        "post_caption": post_of_comment["caption"],
        "profile_pic_url": post_of_comment["media_url"]
    }
    return CommentInfoDto(**data)


if __name__ == '__main__':
    inst_api_client = InstagramApiClient()
    inst_api_client.long_lived_token = ""
    redis_client = RedisClient()
    print(get_new_messages_id(inst_api_client, redis_client))
