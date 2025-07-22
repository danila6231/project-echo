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

router = APIRouter()

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
async def check_auth(session_id: Annotated[str | None, Cookie()] = None):
    """Check if user is authenticated."""
    print(session_id)
    print(Cookie())
    if not session_id:
        return {"authenticated": False}
    
    session = session_manager.get_session(session_id)
    if not session:
        return {"authenticated": False}
    
    return {
        "authenticated": True,
        "user": {
            "username": session.get("username"),
            "account_type": session.get("account_type")
        }
    }

@router.post("/auth/logout")
async def logout(response: Response, session_id: Optional[str] = Cookie(None)):
    """Logout user and clear session."""
    if session_id:
        session_manager.delete_session(session_id)
    
    response.delete_cookie(key="session_id")
    return {"message": "Logged out successfully"} 