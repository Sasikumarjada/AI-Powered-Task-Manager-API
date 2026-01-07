import os
import httpx
import logging
from typing import Dict
from app.exceptions import ExternalAPIError

logger = logging.getLogger(__name__)


class AIService:
    """
    Service for interacting with external AI API.
    
    This implementation uses Anthropic's Claude API to:
    1. Generate concise summaries of task descriptions
    2. Suggest appropriate priority levels based on content analysis
    
    Error Handling:
    - Implements timeout protection (10 seconds)
    - Catches network errors and API failures
    - Provides graceful degradation (app continues without AI features)
    - Includes retry logic for transient failures
    """
    
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.api_url = "https://api.anthropic.com/v1/messages"
        self.timeout = 10.0
        self.max_retries = 2
        
    async def analyze_task(self, title: str, description: str) -> Dict[str, str]:
        """
        Analyze task using AI to generate summary and priority suggestion.
        
        Args:
            title: Task title
            description: Task description
            
        Returns:
            Dict containing 'summary' and 'suggested_priority'
            
        Raises:
            ExternalAPIError: If API call fails after retries
        """
        if not self.api_key:
            logger.warning("ANTHROPIC_API_KEY not set, skipping AI analysis")
            raise ExternalAPIError("AI service not configured")
        
        prompt = f"""Analyze this task and provide:
1. A concise 1-sentence summary (max 100 characters)
2. A suggested priority (low, medium, or high) based on urgency indicators

Task Title: {title}
Task Description: {description}

Respond ONLY with valid JSON in this exact format:
{{"summary": "your summary here", "suggested_priority": "medium"}}"""

        for attempt in range(self.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        self.api_url,
                        headers={
                            "x-api-key": self.api_key,
                            "anthropic-version": "2023-06-01",
                            "content-type": "application/json"
                        },
                        json={
                            "model": "claude-3-5-sonnet-20241022",
                            "max_tokens": 200,
                            "messages": [
                                {
                                    "role": "user",
                                    "content": prompt
                                }
                            ]
                        }
                    )
                    
                    response.raise_for_status()
                    data = response.json()
                    
                    # Extract text from Claude's response
                    content = data.get("content", [{}])[0].get("text", "{}")
                    
                    # Parse JSON response
                    import json
                    result = json.loads(content.strip())
                    
                    # Validate response structure
                    if "summary" not in result or "suggested_priority" not in result:
                        raise ValueError("Invalid AI response format")
                    
                    # Validate priority value
                    valid_priorities = ["low", "medium", "high"]
                    if result["suggested_priority"] not in valid_priorities:
                        result["suggested_priority"] = "medium"
                    
                    logger.info(f"AI analysis successful on attempt {attempt + 1}")
                    return result
                    
            except httpx.TimeoutException:
                logger.warning(f"AI API timeout on attempt {attempt + 1}")
                if attempt == self.max_retries:
                    raise ExternalAPIError("AI service timeout")
                    
            except httpx.HTTPError as e:
                logger.error(f"AI API HTTP error on attempt {attempt + 1}: {e}")
                if attempt == self.max_retries:
                    raise ExternalAPIError(f"AI service error: {str(e)}")
                    
            except (json.JSONDecodeError, ValueError, KeyError) as e:
                logger.error(f"AI response parsing error: {e}")
                if attempt == self.max_retries:
                    raise ExternalAPIError("AI service returned invalid response")
        
        # Fallback (should not reach here)
        raise ExternalAPIError("AI service failed after all retries")
