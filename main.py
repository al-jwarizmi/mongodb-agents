import os
import asyncio
from typing import Dict, List, Optional
from dotenv import load_dotenv
from agents.router_agent import RouterAgent
import logging
from config.logging_config import setup_logging

# Initialize logging
setup_logging()
logger = logging.getLogger('agents.system')

class CustomerSupportSystem:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        logger.info("Initializing Customer Support System")
        
        # Initialize the router agent
        self.router = RouterAgent()
        
        # Maintain conversation history
        self.conversation_history: Dict[str, List[Dict]] = {}
        
    async def process_query(self, query: str, session_id: str = "default") -> str:
        """Process a customer query and return the response."""
        logger.info(f"Processing query for session {session_id}: {query}")
        
        # Initialize conversation history for new sessions
        if session_id not in self.conversation_history:
            logger.debug(f"Initializing new conversation for session {session_id}")
            self.conversation_history[session_id] = []
            
        # Create context with conversation history
        context = {
            "history": self.conversation_history[session_id][-5:] if self.conversation_history[session_id] else []
        }
        logger.debug(f"Context for session {session_id}: {context}")
        
        try:
            # Get response from router agent
            logger.debug("Routing query to router agent")
            response = await self.router.process_message(query, context)
            
            # Update conversation history
            self.conversation_history[session_id].extend([
                {"role": "user", "content": query},
                {"role": "assistant", "content": response}
            ])
            logger.debug(f"Updated conversation history for session {session_id}")
            
            logger.info(f"Successfully processed query for session {session_id}")
            return response
        except Exception as e:
            error_msg = f"An error occurred: {str(e)}"
            logger.error(f"Error processing query: {error_msg}", exc_info=True)
            return error_msg
            
    def clear_conversation(self, session_id: str = "default"):
        """Clear the conversation history for a session."""
        logger.info(f"Clearing conversation history for session {session_id}")
        self.conversation_history[session_id] = []

async def main():
    """Main CLI interface for testing the customer support system."""
    # Initialize the system
    system = CustomerSupportSystem()
    
    print("🤖 Welcome to Frodo - Your Mattress Expert!")
    print("Type 'quit' to exit, 'clear' to start a new conversation\n")
    
    while True:
        try:
            # Get user input
            query = input("\nYou: ").strip()
            
            # Handle commands
            if query.lower() == 'quit':
                logger.info("User requested to quit")
                print("\nGoodbye! 👋")
                break
            elif query.lower() == 'clear':
                logger.info("User requested to clear conversation")
                system.clear_conversation()
                print("\nConversation cleared. Starting fresh! ✨")
                continue
            elif not query:
                continue
                
            # Process query and get response
            print("\nFrodo is thinking... 🤔")
            response = await system.process_query(query)
            print(f"\nFrodo: {response}")
            
        except KeyboardInterrupt:
            logger.info("User interrupted the program")
            print("\n\nGoodbye! 👋")
            break
        except Exception as e:
            logger.error("Unexpected error in main loop", exc_info=True)
            print(f"\n❌ An error occurred: {str(e)}")

if __name__ == "__main__":
    # Run the main CLI interface
    asyncio.run(main()) 