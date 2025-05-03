import base64
from typing import Dict, List, Optional
import openai

from app.core.config import settings
from app.models.output import ContentIdea, OutputResponse

class LLMEngine:
    """Service for interacting with the OpenAI API."""
    
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        self.model = settings.LLM_MODEL
    
    def encode_image(self, image_path: str) -> str:
        """Convert image to base64 for API submission."""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def analyze_account(
        self, 
        image_paths: List[str], 
        account_description: Optional[str] = None
    ) -> Dict:
        """
        Analyze social media account based on images and description.
        Returns content ideas and account summary.
        """
        # Prepare message content with images
        content = [
            {
                "type": "text",
                "text": (
                    "Analyze these screenshots of a social media account and generate content ideas. "
                    "Provide an account summary and 2-3 content ideas with captions and hashtags."
                )
            }
        ]
        
        # Add account description if provided
        if account_description:
            content.append({
                "type": "text",
                "text": f"Account description: {account_description}"
            })
        
        # Add images to content
        for image_path in image_paths:
            base64_image = self.encode_image(image_path)
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }
            })
        
        # Make API call
        response = openai.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a professional social media marketing assistant. "
                        "Analyze the provided screenshots of social media profiles and provide: "
                        "1. A brief summary of the account's content and style. "
                        "2. 2-3 content ideas tailored to the account. "
                        "Each idea should include a title, caption draft, hashtag suggestions, and post theme. "
                        "Be specific and align with the account's existing style and audience."
                    )
                },
                {
                    "role": "user",
                    "content": content
                }
            ],
            max_tokens=2000,
            temperature=0.7
        )
        
        # Parse and structure response
        raw_response = response.choices[0].message.content
        
        # Process the response to extract structured data
        # This is a simplified example - in production you'd have more robust parsing
        lines = raw_response.split('\n')
        account_summary = ""
        content_ideas = []
        
        current_section = "summary"
        current_idea = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if "ACCOUNT SUMMARY" in line.upper():
                current_section = "summary"
                continue
            elif "CONTENT IDEAS" in line.upper() or "CONTENT IDEA" in line.upper():
                current_section = "ideas"
                continue
            elif "IDEA " in line.upper() or "# " in line:
                # Save previous idea if exists
                if current_idea and "title" in current_idea:
                    content_ideas.append(ContentIdea(**current_idea))
                # Start new idea
                current_idea = {"title": line.split(":", 1)[1].strip() if ":" in line else line.strip()}
                continue
                
            if current_section == "summary" and line:
                account_summary += line + " "
            elif current_section == "ideas":
                if "CAPTION:" in line.upper():
                    current_idea["caption_draft"] = line.split(":", 1)[1].strip()
                elif "HASHTAGS:" in line.upper():
                    hashtags = line.split(":", 1)[1].strip()
                    current_idea["hashtag_suggestions"] = [tag.strip() for tag in hashtags.split() if tag.strip()]
                elif "THEME:" in line.upper() or "POST THEME:" in line.upper():
                    current_idea["post_theme"] = line.split(":", 1)[1].strip()
        
        # Add last idea if exists
        if current_idea and "title" in current_idea and "caption_draft" in current_idea and "hashtag_suggestions" in current_idea and "post_theme" in current_idea:
            content_ideas.append(ContentIdea(**current_idea))
            
        # Ensure we have all required fields
        if not account_summary:
            account_summary = "Account analysis based on provided screenshots."
            
        if not content_ideas:
            # Create default content ideas if parsing failed
            content_ideas = [
                ContentIdea(
                    title="Engaging Content Idea",
                    caption_draft="This is a suggested caption based on your content style.",
                    hashtag_suggestions=["#content", "#socialmedia", "#engagement"],
                    post_theme="General engagement post based on your account theme"
                )
            ]
        
        return {
            "account_summary": account_summary.strip(),
            "content_ideas": [idea.dict() for idea in content_ideas]
        }

# Create global LLM engine instance
llm_engine = LLMEngine() 