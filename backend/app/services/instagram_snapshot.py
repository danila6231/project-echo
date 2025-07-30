import requests

from app.infrastructure.instagram_client import InstagramApiClient
from app.infrastructure.openai_client import Chat, OpenAIClient

LONG_LIVED_TOKEN = 'IGAAIJkphRBX5BZAE5FaGNSejhRaWRJZAU14QmRXZAGVMN0stSkNIV1hIQktqZAEQ1enRDNlFiQ0dfbWN6cnVvaklKdmhhX0NqZAFpOd3FrVEtNQlRhclpiSXlBMVNWY1RoZA194VzhGdmU5LVF0VzMzVWZAmbmxR'
IMAGE_STORAGE = "/Users/ivanleskin/Desktop/inst_images"


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


def download_post_image(image_url: str, save_path: str) -> None:
    """
    Download the image from a specific post and save it to a local file.
    """
    if image_url:
        response = requests.get(image_url)
        if response.status_code == 200:
            with open(save_path, 'wb') as file:
                file.write(response.content)


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
    chat.preset_with_instruction("Describe instagram account by next provided posts, comments and private dialogs")

    gpt_client.prompt(chat)
    
    # Fetch detailed posts data
    for post in posts_data.data:
        post_content = client.post_details(post.id)
        prompt_text = post_to_str(post_content)
        if post_content['media_type'] == 'IMAGE':
            # just forward link?
            # download_post_image(post_content['media_url'], f"{IMAGE_STORAGE}/{post.id}.jpeg")
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
    prompt_text = dialogs_to_str(detailed_private_dialogs, user_info.user_id)
    chat.add_prompt(prompt_text)

    description = gpt_client.prompt(chat)

    return description


# if __name__ == '__main__':
#     print(describe_instagram_account(LONG_LIVED_TOKEN))