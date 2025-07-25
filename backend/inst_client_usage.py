from app.infrastructure.instagram_client import InstagramApiClient

CODE = 'AQDlIkHRwpyuymos78lp8n6lT7knAcWdjRw706-bx-z464HdiFlvy6xYhgheywH656tMSV2xrwmGK66xo4tJfSehglKdCIoX1TbzC4LSicH_g8CrlilB3pbacktirTGkqWMNEYJX_HCzpqDJdwB-J4224F-l8mgzycIjmpaaBXxd8F3-FQnzNfR6kPCRqFT-ThMaKA_5qrMk7V6UotAUBwzpMXsobWUfgqG5YEwOL2-WkQ'

SHORT_LIVED_TOKEN = 'IGAAIJkphRBX5BZAE44VWZA5QjcxSHI1TUFJODBUd0didzU3Q0R1UzNkQ201ZA1IwcnJVNzlpZAW8xYzR6eDNtdWwxb2ZA6djR4QU1vQzhua3MzSVJvSHRGUGVNT3ZATUHVNenBhQzhmMkJqZAG1HZA284TUc1anVDUlN4UFBYN3JlSTUySVFRVTFyeW1JSFMxTnV4bV96YThjVUxR'
LONG_LIVED_TOKEN = 'IGAAIJkphRBX5BZAFBVNlFXcXZA0WTNLZAWdsc2F3dUx2c0VvdWdTY0c2eUhra1plWWZABay1TZAzJXbndzNTVtOElfX25wYWpwVGdxbHdpZAzJPWWJRSXhHdmxydTg4MTFraFRpa2FYbW5RMHlzTXU1NXRPeFNR'
USER_ID = 0

if __name__ == "__main__":
    api = InstagramApiClient()
    api.short_lived_token = SHORT_LIVED_TOKEN
    api.long_lived_token = LONG_LIVED_TOKEN

    all_posts = api.get_posts()
    one_post = all_posts.data[0]
    print('one post:', one_post)
    comments = api.get_comments(one_post.id)
    print('comments:', comments)
    user_info = api.get_me_info()
    print('user info:', user_info)
    conversations = api.get_conversations()
    print('conversations:', conversations)
    one_conversation = conversations.data[0]
    dialog = api.get_messages_in_conversation(one_conversation.id)
    print('messages in conversation:', dialog)
    one_message = api.get_message_info(dialog.messages.data[0].id)
    print('message:', one_message)
    conv_with_user = api.get_conversations_with_user(one_message.from_user.id)
    print('conversations with user:', conv_with_user)
    message_response = api.send_text_message(user_info.id, '763080376301282', "Hello World!")
    print('message response:', message_response)

    # api.short_lived_token = SHORT_LIVED_TOKEN
    # api.long_lived_token = LONG_LIVED_TOKEN
    #
    # allPosts = api.posts()
    # print(api.comments(allPosts.data[0].id))

    # api.short_lived_token = SHORT_LIVED_TOKEN
    # api.long_lived_token = LONG_LIVED_TOKEN
    #
    # print(api.get_user_info())
