import traceback

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Response, Cookie, Depends
from fastapi.responses import RedirectResponse
from typing import List, Optional, Annotated
import httpx
from urllib.parse import urlencode

from app.infrastructure.redis_client import RedisClient
from app.models.schemas import ContentIdeasResponse
from app.services.chatgpt_service import ChatGptService
from app.services.instagram_snapshot import get_new_comments_id, get_comment_info_by_id, get_new_messages_id
from app.services.llm_engine import llm_engine
from app.services.token_manager import token_manager
from app.services.context_processor import context_processor
from app.services.session_manager import session_manager
from app.core.config.main_config import settings, Settings
from app.infrastructure.instagram_client import InstagramApiClient

router = APIRouter()
chat_gpt_service = ChatGptService()
settings = Settings()

def get_auth_session(session_id: Annotated[Optional[str], Cookie()] = None):
    """Helper function to check authentication and return session data."""
    if settings.SKIP_LOGIN:
        return {
            "username": settings.TEST_USER_USERNAME,
            "account_type": settings.TEST_USER_ACCOUNT_TYPE,
            "user_id": settings.TEST_USER_ID,
            "access_token": settings.TEST_USER_TOKEN
        }
        
    if not session_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=401, detail="Session expired")
        
    return session

# TODO эндпоинт с анализом аккаунта:
# 1) Пока не смоторим дифф между snapshot контекста об аккаунте, каждый раз полный фетч информации
# 2) Нужен вариант с доступом к переписке и без него (2 уровня точности ответа), пока реализуем только вариант с доступом к переписке
# 3) Придумать дизайн хранения контекста + иметь в виду RAG

# TODO эндпоинт с запросом в чатгпт:
# 1) Актуализация контекста, если необходимо
# 2) Сериализация хранимого контекста и составление запроса
# 3) Сам запрос


# todo: extend responses id openapi doc with HTTP 400 and 500
@router.post("/analyze", response_model=ContentIdeasResponse)
async def analyze_account(
    files: List[UploadFile] = File(..., description="Screenshots of social media profile (1-3 images)"),
    account_description: Optional[str] = Form(None, description="Optional description of the account")
):
    """
    Analyze social media account screenshots and generate content ideas.
    Upload 1-3 screenshots of a social profile and optionally provide a description.
    """
    # Validate file count
    if not files or len(files) > 3:
        raise HTTPException(
            status_code=400, 
            detail="Please provide between 1 and 3 image files"
        )
    
    # Validate file types
    for file in files:
        content_type = file.content_type
        if not content_type or not content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail=f"File {file.filename} is not an image. Please upload only image files."
            )
    
    try:
        # Save uploaded images to temporary files
        image_paths = await context_processor.save_uploaded_images(files)
        
        # Generate a token for this request
        token = token_manager.generate_token()
        
        # Process images with LLM
        result = llm_engine.analyze_account(image_paths, account_description)
        
        # Clean up temporary files
        context_processor.cleanup_temp_files(image_paths)
        
        # Prepare response
        response = ContentIdeasResponse(
            account_summary=result["account_summary"],
            content_ideas=result["content_ideas"],
            token=token
        )
        # Store response in Redis
        token_manager.store_response(token, response.model_dump())
        
        return response
        
    except Exception as e:
        # Clean up any temp files in case of error
        if 'image_paths' in locals():
            context_processor.cleanup_temp_files(image_paths)
        print(str(e))
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing your request: {str(e)}"
        )

@router.get("/result/{token}", response_model=ContentIdeasResponse)
async def get_result(token: str):
    """Retrieve a previously generated result using the token."""
    response = token_manager.get_response(token)
    
    if not response:
        raise HTTPException(
            status_code=404,
            detail="Result not found or expired. Please submit your images again."
        )
    
    return response

@router.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {"status": "ok"}

# Instagram Authentication Endpoints
@router.get("/auth/instagram")
async def instagram_login():
    """Initiate Instagram OAuth flow."""
    params = {
        "force_reauth": "true",
        "client_id": settings.INSTAGRAM_CLIENT_ID,
        "redirect_uri": settings.INSTAGRAM_REDIRECT_URI,
        "scope": "instagram_business_basic,instagram_business_manage_messages,instagram_business_manage_comments,instagram_business_content_publish,instagram_business_manage_insights",
        "response_type": "code"
    }
    auth_url = f"https://www.instagram.com/oauth/authorize?{urlencode(params)}"
    return {"auth_url": auth_url}

# TODO авторизация:
# 1) Внести instagram_client методы
# 2) Пока нет обмена на long-lived, добавить
# 3) Сделать lookup пары user_id: long-lived token в redis на этапе обмена short token на long-lived token
@router.get("/auth/instagram/callback")
async def instagram_callback(code: str):
    """Handle Instagram OAuth callback."""
    try:
        # Exchange code for access token
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                "https://api.instagram.com/oauth/access_token",
                data={
                    "client_id": settings.INSTAGRAM_CLIENT_ID,
                    "client_secret": settings.INSTAGRAM_CLIENT_SECRET,
                    "grant_type": "authorization_code",
                    "redirect_uri": settings.INSTAGRAM_REDIRECT_URI,
                    "code": code
                }
            )
            token_data = token_response.json()
            
            if "access_token" not in token_data:
                # Redirect to frontend with error
                return RedirectResponse(
                    url=f"{settings.FRONTEND_URL}/login?error=auth_failed",
                    status_code=302
                )
            
            access_token = token_data["access_token"]
            user_id = token_data.get("user_id")
            
            # Get user info
            user_response = await client.get(
                f"https://graph.instagram.com/me",
                params={
                    "fields": "id,username,account_type",
                    "access_token": access_token
                }
            )
            user_data = user_response.json()
            
            # Create session
            session_id = session_manager.create_session({
                "user_id": user_id,
                "username": user_data.get("username"),
                "account_type": user_data.get("account_type"),
                "access_token": access_token
            })
            
            # Create redirect response with session cookie
            redirect_response = RedirectResponse(
                url=settings.FRONTEND_URL,
                status_code=302
            )
            
            # Set session cookie
            redirect_response.set_cookie(
                key="session_id",
                value=session_id,
                httponly=True,
                secure=settings.COOKIE_SECURE,
                samesite="none",
                max_age=settings.SESSION_EXPIRY
            )
            
            return redirect_response
            
    except Exception as e:
        # Redirect to frontend with error
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/login?error={str(e)}",
            status_code=302
        )

@router.get("/auth/check")
async def check_auth(session_id: Annotated[Optional[str], Cookie()] = None):
    """Check if user is authenticated."""
    try:
        session = get_auth_session(session_id)
        return {
            "authenticated": True,
            "user": {
                "username": session.get("username"),
                "account_type": session.get("account_type")
            }
        }
    except HTTPException:
        return {"authenticated": False}

@router.post("/auth/logout")
async def logout(response: Response, session_id: Optional[str] = Cookie(None)):
    """Logout user and clear session."""
    if session_id:
        session_manager.delete_session(session_id)
    
    response.delete_cookie(key="session_id")
    return {"message": "Logged out successfully"}

# Mock endpoints for comment analysis feature
@router.get("/comments/latest")
async def get_latest_comments(session: dict = Depends(get_auth_session)):
    """Fetch latest comments from user's Instagram posts."""
    try:
        # Initialize Instagram client
        inst_api_client = InstagramApiClient()
        redis_client = RedisClient()
        
        # Set the long-lived token from session
        access_token = session.get("access_token")
        if not access_token:
            raise HTTPException(status_code=401, detail="Access token not found or session expired")
        
        inst_api_client.long_lived_token = access_token
        inst_api_client.user_id = session.get("user_id")

        new_comment_ids = get_new_comments_id(inst_api_client, redis_client)
        new_comment_ids = new_comment_ids if new_comment_ids else []

        new_comments = [(get_comment_info_by_id(inst_api_client, comment_id).model_dump(), new_flg) for comment_id, new_flg in new_comment_ids]
        new_comments.sort(key=lambda comment: comment[0]["timestamp"], reverse=True)
        return {"comments": new_comments, "is_mock": False}
            
    except Exception as e:
        print(f"Error fetching Instagram comments: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

# @router.get("/comments/latest-single")
# async def get_latest_comment(session: dict = Depends(get_auth_session)):
#     """Fetch latest comment from user's Instagram account."""
#     # Get all comments and return just the first one
#     comments_response = await get_latest_comments(session)
#     comments = comments_response.get("comments", [])
    
#     if comments:
#         return {"comment": comments[0]}
#     else:
#         # Return a single mock comment if no comments found
#         return {
#             "comment": {
#                 "id": "mock_comment_123",
#                 "text": "Love your content! Can you share more tips about healthy eating?",
#                 "username": "fitness_enthusiast_22",
#                 "timestamp": "2024-01-15T14:30:00Z",
#                 "post_id": "mock_post_456",
#                 "post_caption": "5 Easy Ways to Start Your Fitness Journey 💪 #fitness #healthylifestyle",
#                 "profile_pic_url": "https://via.placeholder.com/50"
#             }
#         }

@router.post("/comments/suggest-reply")
async def suggest_comment_reply(
    post_id: str = Form(...),
    comment_id: str = Form(...),
    session: dict = Depends(get_auth_session)
):
    ## TODO: Add the post_id to the query context
    """Generate a reply suggestion based on account analysis."""
    print(f'Suggest comment session_id: {comment_id}; session: {session}')

    access_token = session.get("access_token")
    user_id = session.get("user_id")

    if not access_token:
        raise HTTPException(status_code=401, detail="Access token not found or session expired")

    if not access_token:
        raise HTTPException(status_code=401, detail="User id not found or session expired")

    inst_client = InstagramApiClient()
    inst_client.long_lived_token = access_token

    comment_details = inst_client.comment_details(comment_id)
    
    # print('Comment details:', comment_details)

    replies = []

    for _ in range(3):
        print(f'Start new reply: user_id = {user_id}; token = {access_token} ;comment_text = {comment_details["text"]}')
        new_reply = chat_gpt_service.handle_incoming_interaction(
            user_id,
            access_token,
            comment_details['text'],
            
        )
        # print('New reply to comment:', new_reply)
        replies.append(new_reply)

    # Mock reply suggestion based on "account analysis"
    # todo:
    #  нужен логин адекватный чтобы тестить acess_token,
    #  пока дурацкий мок от фронта приходит
    #  (inst_client.long_lived_token = access_token)
    return {
        "suggested_reply": {
            "text": replies[0],
            "tone": "todo: убрать поле",
            "includes_cta": True,
            "analysis": {
                "account_type": "todo: убрать поле",
                "engagement_strategy": "todo: убрать поле",
                "personalization": "todo: убрать поле"
            }
        },
        "alternative_replies": [
            {
                "text": replies[1],
                "tone": "todo: убрать поле"
            },
            {
                "text": replies[2],
                "tone": "todo: убрать поле"
            }
        ]
    }

@router.post("/messages/suggest-reply")
async def suggest_message_reply(
    message_id: str = Form(...),
    session: dict = Depends(get_auth_session)
):
    """Generate a message reply suggestion based on account analysis."""
    print(f'Suggest message; message: {message_id}; session: {session}')

    access_token = session.get("access_token")
    user_id = session.get("user_id")

    if not access_token:
        raise HTTPException(status_code=401, detail="Access token not found or session expired")

    if not access_token:
        raise HTTPException(status_code=401, detail="User id not found or session expired")

    inst_client = InstagramApiClient()
    inst_client.long_lived_token = access_token

    message_details = inst_client.get_message_info(message_id)
    # print('Message details:', message_details)

    replies = []

    for _ in range(3):
        print(f'Start new reply: user_id = {user_id}; token = {access_token} ;comment_text = {message_details.message}')
        new_reply = chat_gpt_service.handle_incoming_interaction(
            user_id,
            access_token,
            message_details.message
        )
        # print('New reply to message:', new_reply)
        replies.append(new_reply)

    # Mock reply suggestion based on "account analysis"
    # TODO: отдавать просто text, все остальное пока опустить, синкануть с фронтом
    return {
        "suggested_reply": {
            "text": replies[0],
            "tone": "todo: убрать поле",
            "includes_cta": True,
            "analysis": {
                "account_type": "todo: убрать поле",
                "engagement_strategy": "todo: убрать поле",
                "personalization": "todo: убрать поле"
            }
        },
        "alternative_replies": [
            {
                "text": replies[1],
                "tone": "todo: убрать поле"
            },
            {
                "text": replies[2],
                "tone": "todo: убрать поле"
            }
        ]
    }


@router.get("/message/latest")
async def get_latest_messages(session: dict = Depends(get_auth_session)):
    """Fetch latest messages from user's Instagram Direct."""
    try:
        # Initialize Instagram client
        inst_api_client = InstagramApiClient()
        redis_client = RedisClient()

        # Set the long-lived token from session
        access_token = session.get("access_token")
        if not access_token:
            raise HTTPException(status_code=401, detail="Access token not found or session expired")

        inst_api_client.long_lived_token = access_token
        inst_api_client.user_id = session.get("user_id")

        new_message_ids = get_new_messages_id(inst_api_client, redis_client)
        new_message_ids = new_message_ids if new_message_ids else []
        
        # new_comments = [(get_comment_info_by_id(comment_id).model_dump(), new_flg) for comment_id, new_flg in new_comment_ids]
        # new_comments.sort(key=lambda comment: comment[0]["timestamp"], reverse=True)

        new_and_stale_messages = [(inst_api_client.get_message_info(msg_id), new_flg) for msg_id, new_flg in new_message_ids]
        new_and_stale_messages.sort(key=lambda message: message[0].created_time, reverse=True)
        # print(f'New messages: {new_and_stale_messages}')
        return {"messages": new_and_stale_messages, "is_mock": False}
    except Exception as e:
        print(f"Error fetching Instagram messages: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
