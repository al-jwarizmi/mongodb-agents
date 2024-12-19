"""Base agent for the Sleep Better customer support system."""
from typing import Dict, List, Optional, Any, Callable
import os
import logging
from functools import wraps
from database.mongodb_client import MongoDB
from dotenv import load_dotenv
from pathlib import Path
from openai import AsyncOpenAI

# Load environment variables from config/.env file
load_dotenv(Path(__file__).parent.parent / 'config' / '.env')

logger = logging.getLogger('agents.base')

class BaseAgent:
    """Base class for all agents in the system."""
    
    @staticmethod
    def function_spec(name: str, description: str, parameters: Dict):
        """Decorator to specify function metadata for agents."""
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            
            wrapper.function_spec = {
                "name": name,
                "description": description,
                "parameters": parameters
            }
            return wrapper
        return decorator
    
    def __init__(self, name: str = "BaseAgent"):
        """Initialize the base agent."""
        self.name = name
        self.available_functions = {}
        self.db = MongoDB()
        
        # Initialize OpenAI client
        self.client = AsyncOpenAI(
            api_key=os.getenv('OPENAI_API_KEY')
        )
        
        self._register_functions()
        logger.info(f"Initialized {self.__class__.__name__} with OpenAI client")
        
    def _create_system_prompt(self) -> str:
        """Create the system prompt for the agent."""
        return f"""You are {self.name}, a specialized customer support agent.
        Your role is to assist customers with their inquiries in a friendly and professional manner.
        Always maintain a helpful and positive tone, and provide accurate information."""
        
    def _register_functions(self):
        """Register available functions for the agent."""
        pass
        
    async def process_message(self, message: str, context: Optional[Dict] = None) -> str:
        """Process an incoming message and return a response."""
        try:
            # Create messages for OpenAI
            messages = [
                {"role": "system", "content": self._create_system_prompt()},
                {"role": "user", "content": message}
            ]
            
            # Add context if provided
            if context and context.get('history'):
                messages[1:1] = context['history']
            
            logger.debug(f"Sending message to OpenAI: {messages}")
            
            # Get response from OpenAI
            response = await self.client.chat.completions.create(
                model=os.getenv('GPT_MODEL', 'gpt-4'),
                messages=messages,
                temperature=float(os.getenv('TEMPERATURE', '0.7'))
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}", exc_info=True)
            return "I apologize, but I encountered an error processing your request. Please try again."
            
    def get_function_specs(self) -> Dict[str, Dict[str, Any]]:
        """Get specifications for all registered functions."""
        specs = {}
        for name, func in self.available_functions.items():
            if hasattr(func, 'function_spec'):
                specs[name] = func.function_spec
        return specs

    def is_enabled(self) -> bool:
        """Check if the agent is enabled in configuration."""
        return os.getenv(f'ENABLE_{self.name.upper().replace(" ", "_")}', 'true').lower() == 'true'