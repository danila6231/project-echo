import base64
from typing import Dict, List, Optional
import openai

from app.core.config import settings
from app.models.output import ContentIdea, OutputResponse
from pydantic import BaseModel


client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

class ContentIdeasList(BaseModel):
    content_ideas: List[ContentIdea]
    
SYSTEM_INSTRUCTIONS = """
# Identity

You are helpful, friendly and creative SMM assistant that helps social media account owners to come up with content ideas.

# Instructions

* Never mention that you are AI, your responses will NEVER include warnings, disclaimers, etc. such as, but not limited to, "As an Al", "As a large language mode" "As an artificial intelligence, I don't have feelings or emotions" The user already knows you are an LLM. Just skip to the answer.
* Never use complex language, remember that you are a social media assistant, so never use language more advanced than the one used commonly on social media
* DO NOT use the "—" character EVER in you outputs
* Your answer must be directly an answer to the question. If you have nothing to answer - return empty answer
"""

SUMMARY_INSTRUCTIONS = """
Analyze these screenshots of a social media account and additional description by account's owner if provided and give a short one paragraph summary of the account topic.

Your conclusions about accounts purpose could be inaccurate, so don't use definitive statements. 
"""

CONTENT_IDEAS_INSTRUCTIONS = """
Generate 5-7 content ideas that align with the provided account description and style.
Attached screenshots of the account might be provided to help you understand the account.
Each idea should include:
* content_type: Type of the content (e.g. post, story, reel, etc.);
* title: A clear title;
* theme: Theme or concept: no more that 10 words;
* caption_draft: An engaging caption draft: don't make it too long;
* hashtag_suggestions: Relevant hashtag suggestions;
* reason: Reason why this idea is relevant to the account and might be engaging for the audience: 1-2 short sentences.

Make each idea distinct and tailored to the account's aesthetic and audience.
"""

class LLMEngine:
    """Service for interacting with the OpenAI API."""
    
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        self.model = settings.LLM_MODEL
    
    def _encode_image(self, image_path: str) -> str:
        """Convert image to base64 for API submission."""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def _get_account_summary(
        self,
        image_paths: List[str],
        account_description: Optional[str] = None
    ) -> str:
        """
        Analyze social media account based on images and description.
        Returns a summary of the account's content and style.
        """
        # Prepare message content with images
        content = [
            {
                "type": "input_text",
                "text": SUMMARY_INSTRUCTIONS
            }
        ]
        
        if account_description:
            content.append({
                "type": "input_text",
                "text": f"Account description by account's owner: {account_description}"
            })
        
        for image_path in image_paths:
            base64_image = self._encode_image(image_path)
            content.append({
                "type": "input_image",
                "image_url": f"data:image/jpeg;base64,{base64_image}"
            })
        
        # Make API call for account summary

        response = client.responses.create(
            model=self.model,
            input=[
                {
                "role": "system",
                "content": [
                    {
                    "type": "input_text",
                    "text": SYSTEM_INSTRUCTIONS
                    }
                ]
                },
                {
                "role": "user",
                "content": content
                }
            ],
            text={
                "format": {
                "type": "text"
                }
            },
            temperature=0.7,
            max_output_tokens=1000
        )
        
        result = response.output_text
        
        return result

    def _generate_content_ideas(
        self,
        account_summary: str,
        image_paths: List[str],
        account_description: Optional[str] = None
    ) -> List[ContentIdea]:
        """
        Generate content ideas based on account summary and images.
        Returns a list of content ideas with captions and hashtags.
        """
        # Prepare message content with account summary and images
        content = [
            {
                "type": "input_text",
                "text": CONTENT_IDEAS_INSTRUCTIONS
            }
        ]
        
        if account_description:
            content.append({
                "type": "input_text",
                "text": f"Additional account context: {account_description}"
            })
        
        for image_path in image_paths:
            base64_image = self._encode_image(image_path)
            content.append({
                "type": "input_image",
                "image_url": f"data:image/jpeg;base64,{base64_image}"
            })
            
        response = client.responses.parse(
            model=self.model,
            input=[
                {
                "role": "system",
                "content": [
                    {
                    "type": "input_text",
                    "text": SYSTEM_INSTRUCTIONS
                    }
                ]
                },
                {
                "role": "user",
                "content": content
                }
            ],
            text_format=ContentIdeasList,
            temperature=0.7
            #max_output_tokens=1000
        )
        
        content_ideas = response.output_parsed
        
        # Create default content idea if parsing failed
        if not content_ideas:
            content_ideas = [
                ContentIdea(
                    content_type="post",
                    title="Engaging Content Idea",
                    theme="General engagement post based on your account theme",
                    caption_draft="This is a suggested caption based on your content style.",
                    hashtag_suggestions=["#content", "#socialmedia", "#engagement"],
                    reason="This idea is relevant to the account and might be engaging for the audience"
                )
            ]
        
        return content_ideas
    
    def analyze_account(
        self, 
        image_paths: List[str], 
        account_description: Optional[str] = None
    ) -> Dict:
        """
        Analyze social media account based on images and description.
        Returns content ideas and account summary.
        """
        # Get account summary
        account_summary = self._get_account_summary(image_paths, account_description)
        
        # Generate content ideas based on the summary
        content_ideas = self._generate_content_ideas(account_summary, image_paths, account_description)
        
        return {
            "account_summary": account_summary,
            "content_ideas": content_ideas
        }

# Create global LLM engine instance
llm_engine = LLMEngine() 