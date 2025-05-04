from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from typing import List, Optional

from app.models.user_input import UserInput
from app.models.output import OutputResponse
from app.services.llm_engine import llm_engine
from app.services.token_manager import token_manager
from app.services.context_processor import context_processor

router = APIRouter()

@router.post("/analyze", response_model=OutputResponse)
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
        response = OutputResponse(
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

@router.get("/result/{token}", response_model=OutputResponse)
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