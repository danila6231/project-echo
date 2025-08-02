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
        prompt_text += " and related image"
    print(f"prompt post: {prompt_text}")
    return prompt_text


def comment_to_str(comment_json) -> str:
    comment_text = comment_json['text']
    prompt_text = f'Comment from user: "{comment_text}"'
    print(f"prompt comment: {prompt_text}")
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
    print(f"prompt dialog: {prompt_text}")
    return prompt_text

def describe_instagram_account(token: str) -> str:
    """
    Description consists of:
    1) posts data
    2) replies to comments
    3) private dialogs
    """

    client = InstagramApiClient().with_long_lived_token(token)
    
    # Fetch posts data
    posts_data = client.get_posts()
    user_info = client.get_me_info()

    # Start providing context
    gpt_client = OpenAIClient()
    chat = Chat()
    chat.preset_with_instruction("Describe instagram account by next provided posts, comments and private dialogs.")

    gpt_client.prompt(chat)
    
    # Fetch detailed posts data
    for post in posts_data.data:
        post_content = client.post_details(post.id)
        prompt_text = post_to_str(post_content)
        if post_content['media_type'] == 'IMAGE':
            chat.add_prompt(prompt_text, post_content['media_url'])

    detailed_posts_data = [client.post_details(post.id) for post in posts_data.data]
    
    # Fetch detailed comments for each post
    for post in posts_data.data:
        comments = client.get_comments(post.id)
        for comment in comments.data:
            comment_detailed = client.comment_details(comment.id)
            prompt_text = comment_to_str(comment_detailed)
            chat.add_prompt(prompt_text)
    
    # Fetch private dialogs
    private_dialogs = client.get_conversations()
    
    # Fetch detailed private dialogs
    detailed_private_dialogs = [client.private_dialog_details(dialog.id) for dialog in private_dialogs.data]

    print(f"dialogs: {detailed_private_dialogs}")
    prompt_text = dialogs_to_str(detailed_private_dialogs, user_info.user_id)
    chat.add_prompt(prompt_text)

    description = gpt_client.prompt(chat)

    return description


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
def get_comment_info_by_id(comment_id: str) -> CommentInfoDto:
    with InstagramApiClient() as instagram_client:
        instagram_client.long_lived_token = LONG_LIVED_TOKEN
        comment_detailed = instagram_client.comment_details(comment_id)
        print(comment_detailed)
        post_of_comment = instagram_client.post_details(comment_detailed["media"]["id"])
        print(post_of_comment)

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
    inst_api_client.long_lived_token = LONG_LIVED_TOKEN
    redis_client = RedisClient()
    print(get_new_messages_id(inst_api_client, redis_client))