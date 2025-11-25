"""
Gemini API client wrapper
Handles all interactions with Google Gemini 3 Pro
"""

import os
from typing import Optional, Dict, Any
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()


class GeminiClient:
    """
    Wrapper for Google Gemini API

    Features:
    - API key management
    - Model configuration
    - Error handling
    - Response parsing
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "gemini-flash-latest",
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ):
        """
        Initialize Gemini client

        Args:
            api_key: Gemini API key (defaults to env var GEMINI_API_KEY)
            model_name: Model to use (default: gemini-1.5-pro)
            temperature: Response creativity (0.0-1.0)
            max_tokens: Max response length
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY not found. Set it in .env file or pass as parameter."
            )

        # Configure API
        genai.configure(api_key=self.api_key)

        # Model configuration
        self.generation_config = {
            "temperature": temperature,
            "max_output_tokens": max_tokens,
            "top_p": 0.95,
            "top_k": 40,
        }

        # Initialize model
        self.model = genai.GenerativeModel(
            model_name=model_name, generation_config=self.generation_config
        )

        print(f"Gemini client initialized (model: {model_name})")

    def query(
        self, prompt: str, system_instruction: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a query to Gemini and get response

        Args:
            prompt: User query + context
            system_instruction: Optional system instruction

        Returns:
            Dict with response and metadata:
            {
                'text': str,
                'success': bool,
                'error': Optional[str],
                'tokens_used': int
            }
        """
        try:
            # Build full prompt
            if system_instruction:
                full_prompt = f"{system_instruction}\n\n{prompt}"
            else:
                full_prompt = prompt

            # Generate response
            response = self.model.generate_content(full_prompt)

            # Parse response
            return {
                "text": response.text,
                "success": True,
                "error": None,
                "tokens_used": self._estimate_tokens(full_prompt, response.text),
            }

        except Exception as e:
            return {"text": "", "success": False, "error": str(e), "tokens_used": 0}

    def _estimate_tokens(self, prompt: str, response: str) -> int:
        """Rough token estimation (1 token ≈ 4 chars)"""
        total_chars = len(prompt) + len(response)
        return total_chars // 4

    def test_connection(self) -> bool:
        """Test if API connection works"""
        try:
            response = self.query("Say 'Hello' in Portuguese")
            return response["success"] and "olá" in response["text"].lower()
        except:
            return False


# Convenience function
def create_client(temperature: float = 0.7, max_tokens: int = 2000) -> GeminiClient:
    """Create a pre-configured Gemini client"""
    return GeminiClient(temperature=temperature, max_tokens=max_tokens)
