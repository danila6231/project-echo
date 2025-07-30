from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Response, Cookie, Depends
from fastapi.responses import RedirectResponse
from typing import List, Optional, Annotated
import secrets
import httpx
from urllib.parse import urlencode

from app.models.schemas import ContentIdeasResponse
from app.services.llm_engine import llm_engine
from app.services.token_manager import token_manager
from app.services.context_processor import context_processor
from app.services.session_manager import session_manager
from app.core.config.main_config import settings
from app.infrastructure.instagram_client import InstagramApiClient

router = APIRouter()

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
    print(auth_url)
    return {"auth_url": auth_url}

# TODO авторизация:
# 1) Внести instagram_client методы
# 2) Пока нет обмена на long-lived, добавить
# 3) Сделать lookup пары user_id: long-lived token в redis на этапе обмена short token на long-lived token
@router.get("/auth/instagram/callback")
async def instagram_callback(code: str):
    """Handle Instagram OAuth callback."""
    try:
        with InstagramApiClient() as instagram_client:
            # Exchange code for access token
            instagram_client.get_short_lived_token(code)
            long_lived_token = instagram_client.get_long_lived_token()
            user_info = instagram_client.get_me_info()

            # Create session
            session_id = session_manager.create_session({
                "user_id": user_info.user_id,
                "username": user_info.username,
                "account_type": user_info.account_type,
                "access_token": long_lived_token
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
                samesite="none" if settings.COOKIE_SECURE else "lax",
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
    
    # Mock data for fallback
    mock_comments = [
        {
            "id": "mock_comment_1",
            "text": "Love your content! Can you share more tips about healthy eating?",
            "username": "fitness_enthusiast_22",
            "timestamp": "2024-01-15T14:30:00Z",
            "post_id": "mock_post_456",
            "post_caption": "5 Easy Ways to Start Your Fitness Journey 💪 #fitness #healthylifestyle",
            "profile_pic_url": "https://via.placeholder.com/50"
        },
        {
            "id": "mock_comment_2",
            "text": "This is exactly what I needed today! Thank you for the motivation 🙌",
            "username": "wellness_warrior",
            "timestamp": "2024-01-15T12:15:00Z",
            "post_id": "mock_post_457",
            "post_caption": "Morning routine that changed my life ☀️ #morningroutine #wellness",
            "profile_pic_url": "https://via.placeholder.com/50"
        },
        {
            "id": "mock_comment_3",
            "text": "Could you make a video tutorial on this? Would love to learn more!",
            "username": "curious_learner",
            "timestamp": "2024-01-15T10:45:00Z",
            "post_id": "mock_post_458",
            "post_caption": "My secret to staying productive all day 📈 #productivity #mindset",
            "profile_pic_url": "https://via.placeholder.com/50"
        }
    ]
    
    try:
        # Initialize Instagram client
        client = InstagramApiClient()
        
        # Set the long-lived token from session
        access_token = session.get("access_token")
        if not access_token:
            # Return mock data if no access token
            return {"comments": mock_comments, "is_mock": True}
        
        client.long_lived_token = access_token
        client.user_id = session.get("user_id")
        
        # Get user's posts
        posts_response = client.get_posts()
        
        if not posts_response.data:
            # Return mock data if no posts
            return {"comments": mock_comments, "is_mock": True}
        
        # Collect comments from recent posts
        all_comments = []
        posts_with_captions = {}  # Store post captions for later use
        
        # Limit to first 5 posts to avoid too many API calls
        for post in posts_response.data[:5]:
            try:
                # Get post details including caption
                post_url = f"https://graph.instagram.com/v23.0/{post.id}"
                post_params = {
                    "fields": "caption,timestamp",
                    "access_token": client.long_lived_token
                }
                
                import httpx
                async with httpx.AsyncClient() as http_client:
                    post_response = await http_client.get(post_url, params=post_params)
                    if post_response.status_code == 200:
                        post_data = post_response.json()
                        posts_with_captions[post.id] = {
                            "caption": post_data.get("caption", ""),
                            "timestamp": post_data.get("timestamp", "")
                        }
                
                # Get comments for this post
                comments_response = client.get_comments(post.id)
                
                if comments_response.data:
                    for comment in comments_response.data:
                        # Get comment details
                        comment_url = f"https://graph.instagram.com/v23.0/{comment.id}"
                        comment_params = {
                            "fields": "text,username,timestamp",
                            "access_token": client.long_lived_token
                        }
                        
                        comment_response = await http_client.get(comment_url, params=comment_params)
                        if comment_response.status_code == 200:
                            comment_data = comment_response.json()
                            
                            all_comments.append({
                                "id": comment.id,
                                "text": comment_data.get("text", ""),
                                "username": comment_data.get("username", ""),
                                "timestamp": comment_data.get("timestamp", ""),
                                "post_id": post.id,
                                "post_caption": posts_with_captions.get(post.id, {}).get("caption", ""),
                                "profile_pic_url": f"https://graph.instagram.com/v23.0/{comment_data.get('username', '')}/picture"
                            })
                            
            except Exception as e:
                print(f"Error fetching comments for post {post.id}: {str(e)}")
                continue
        
        if all_comments:
            # Sort by timestamp (newest first)
            all_comments.sort(key=lambda x: x["timestamp"], reverse=True)
            # Return up to 10 latest comments
            return {"comments": all_comments[:10], "is_mock": False}
        else:
            # Return mock data if no comments found
            return {"comments": mock_comments, "is_mock": True}
            
    except Exception as e:
        print(f"Error fetching Instagram comments: {str(e)}")
        # Return mock data on error
        return {"comments": mock_comments, "is_mock": True, "error": str(e)}

@router.get("/comments/latest-single")
async def get_latest_comment(session: dict = Depends(get_auth_session)):
    """Fetch latest comment from user's Instagram account."""
    # Get all comments and return just the first one
    comments_response = await get_latest_comments(session)
    comments = comments_response.get("comments", [])
    
    if comments:
        return {"comment": comments[0]}
    else:
        # Return a single mock comment if no comments found
        return {
            "comment": {
                "id": "mock_comment_123",
                "text": "Love your content! Can you share more tips about healthy eating?",
                "username": "fitness_enthusiast_22",
                "timestamp": "2024-01-15T14:30:00Z",
                "post_id": "mock_post_456",
                "post_caption": "5 Easy Ways to Start Your Fitness Journey 💪 #fitness #healthylifestyle",
                "profile_pic_url": "https://via.placeholder.com/50"
            }
        }

@router.post("/comments/suggest-reply")
async def suggest_comment_reply(
    comment_id: str = Form(...),
    session: dict = Depends(get_auth_session)
):
    """Generate a reply suggestion based on account analysis."""
    # Mock reply suggestion based on "account analysis"
    return {
        "suggested_reply": {
            "text": "Thank you so much! 🙏 I'd love to share more healthy eating tips! Check out my latest post on meal prep basics, and stay tuned for a detailed guide on balanced nutrition coming next week! What specific aspect of healthy eating interests you most?",
            "tone": "friendly and engaging",
            "includes_cta": True,
            "analysis": {
                "account_type": "Health & Fitness Influencer",
                "engagement_strategy": "Building community through questions and valuable content",
                "personalization": "References recent content and promises future value"
            }
        },
        "alternative_replies": [
            {
                "text": "Thanks for the love! 💚 Absolutely! Tomorrow I'm dropping my top 10 healthy eating hacks. Any particular area you're struggling with?",
                "tone": "casual and helpful"
            },
            {
                "text": "I appreciate your support! ✨ I've got a whole series on healthy eating coming up. Follow along and don't miss the meal prep guide this Friday!",
                "tone": "professional and informative"
            }
        ]
    } 