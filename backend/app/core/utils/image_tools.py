from PIL import Image
import io

def validate_image(image_data: bytes) -> bool:
    """
    Validates if the provided bytes represent a valid image.
    
    Args:
        image_data: Binary image data
        
    Returns:
        bool: True if valid image, False otherwise
    """
    try:
        img = Image.open(io.BytesIO(image_data))
        img.verify()  # Verify image data integrity
        return True
    except Exception:
        return False

def resize_image_if_needed(image_data: bytes, max_size: int = 4 * 1024 * 1024) -> bytes:
    """
    Resizes an image if it exceeds the specified maximum size.
    
    Args:
        image_data: Binary image data
        max_size: Maximum allowed size in bytes (default 4MB)
        
    Returns:
        bytes: Processed image data
    """
    # If image is already small enough, return as is
    if len(image_data) <= max_size:
        return image_data
    
    # Open image and prepare for resizing
    img = Image.open(io.BytesIO(image_data))
    
    # Keep original format
    format = img.format or 'JPEG'
    
    # Calculate scaling factor based on image size
    scale_factor = 0.9  # Start with 90% reduction
    
    # Try reducing quality and size until we get under max_size
    quality = 95
    output = io.BytesIO()
    
    while True:
        # Resize image
        new_width = int(img.width * scale_factor)
        new_height = int(img.height * scale_factor)
        resized_img = img.resize((new_width, new_height), Image.LANCZOS)
        
        # Save to buffer
        output = io.BytesIO()
        resized_img.save(output, format=format, quality=quality)
        
        # Check size
        new_size = output.tell()
        if new_size <= max_size or quality <= 70 or scale_factor <= 0.5:
            # Stop if size is acceptable or we've reduced quality/scale too much
            break
            
        # Adjust parameters for next attempt
        if quality > 70:
            quality -= 5
        else:
            scale_factor *= 0.9
            
        output.seek(0)
    
    # Return the resized image data
    return output.getvalue() 