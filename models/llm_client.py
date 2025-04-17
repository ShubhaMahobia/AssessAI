import google.generativeai as genai
import os
from typing import Dict, Any


class LLMClient:
    """Client for interacting with the Gemini LLM API."""
    
    def __init__(self, api_key: str = None, model_name: str = "gemini-1.5-flash"):
        """Initialize the LLM client.
        
        Args:
            api_key: Google API key for Gemini access
            model_name: Name of the model to use
        """
        # API key handling
        if api_key:
            self.api_key = api_key
        else:
            self.api_key = os.environ.get("GOOGLE_API_KEY")
            
        if not self.api_key:
            raise ValueError("Google API key is required")
            
        # Configure Gemini API
        genai.configure(api_key=self.api_key)
        
        # Initialize the model using the specified model
        self.model = genai.GenerativeModel(
            model_name=model_name,
            generation_config={
                "temperature": 0.8,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 1024,
            }
        )
        
        # Initialize chat history
        self.chat_session = self.model.start_chat(history=[])
        
    def generate_response(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """Generate a response using the LLM.
        
        Args:
            prompt: Instruction prompt for the model
            context: Additional context for the model
            
        Returns:
            Generated response text
        """
        try:
            # Format prompt with context values if provided
            if context:
                try:
                    formatted_prompt = prompt.format(**context)
                except KeyError:
                    formatted_prompt = prompt
            else:
                formatted_prompt = prompt
            
            # Generate response
            response = self.model.generate_content(formatted_prompt)
            
            if response and hasattr(response, 'text'):
                return response.text.strip()
            return ""
        except Exception as e:
            print(f"Error generating response: {str(e)}")
            return ""
            
    def add_to_history(self, user_message: str, bot_message: str) -> None:
        """Add messages to chat history.
        
        Args:
            user_message: Message from the user
            bot_message: Response from the bot
        """
        self.chat_session.history.append({"role": "user", "parts": [user_message]})
        self.chat_session.history.append({"role": "model", "parts": [bot_message]})
        
    def get_chat_history(self):
        """Get the chat history.
        
        Returns:
            Chat history
        """
        return self.chat_session.history
        
    def reset_chat(self) -> None:
        """Reset the chat session."""
        self.chat_session = self.model.start_chat(history=[]) 