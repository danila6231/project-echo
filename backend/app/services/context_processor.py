import os
import tempfile
from fastapi import UploadFile
from typing import List

class ContextProcessor:
    """Processes and prepares user inputs for LLM analysis."""
    
    @staticmethod
    async def save_uploaded_images(files: List[UploadFile]) -> List[str]:
        """
        Save uploaded image files to temporary location.
        Returns a list of temporary file paths.
        """
        temp_image_paths = []
        
        for file in files:
            # Create a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
                # Read image content
                content = await file.read()
                # Write content to temp file
                temp_file.write(content)
                # Add file path to list
                temp_image_paths.append(temp_file.name)
        
        return temp_image_paths
    
    @staticmethod
    def cleanup_temp_files(file_paths: List[str]) -> None:
        """Delete temporary files after processing."""
        for path in file_paths:
            try:
                os.remove(path)
            except Exception:
                # Just log the error and continue if file can't be removed
                pass

# Create global context processor
context_processor = ContextProcessor() 