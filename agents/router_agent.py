"""Router agent for directing queries to appropriate specialized agents."""
from typing import Dict, List, Optional, Type
from .base_agent import BaseAgent
from .product_details_agent import ProductDetailsAgent
from .reviews_agent import ReviewsAgent
from .orders_agent import OrdersAgent
import logging
import os
import json

# Configure logging
logger = logging.getLogger('agents.router')

class RouterAgent(BaseAgent):
    def __init__(self):
        super().__init__("Router")
        self.available_agents: Dict[str, Type[BaseAgent]] = {
            "product_details": ProductDetailsAgent,
            "reviews": ReviewsAgent,
            "orders": OrdersAgent
        }
        self.agent_instances: Dict[str, BaseAgent] = {}
        logger.info(f"Initialized {self.__class__.__name__} with {len(self.available_agents)} available agents")
        
    def _create_system_prompt(self) -> str:
        return """You are a router agent that directs customer queries to specialized agents.

AVAILABLE AGENTS:
1. Product Details Agent
   - Product information, features, specifications
   - Price inquiries
   - Product comparisons
   - Technical questions
   KEYWORDS: features, specs, compare, difference, price, size, material

2. Reviews Agent
   - Customer feedback and experiences
   - Ratings and review analysis
   - Customer satisfaction metrics
   KEYWORDS: reviews, ratings, feedback, customers say, experience, recommend

3. Orders Agent
   - Purchase processing
   - Order status and tracking
   - Shipping and delivery
   - Payment handling
   KEYWORDS: buy, order, purchase, delivery, shipping, payment, track

ROUTING RULES:
1. Order Process Priority:
   - ANY purchase intent → Orders Agent
   - ANY order details → Orders Agent
   - STAY with Orders Agent until order complete

2. Context Awareness:
   - Check conversation history for active orders
   - Maintain agent continuity when appropriate
   - Consider multi-step interactions

3. Quick Routing Guide:
   Product Details → Compare products, specifications
   Reviews → Customer feedback, experiences
   Orders → Purchase intent, order status

4. Default Behaviors:
   - Product comparisons → Product Details first
   - Purchase intent → Orders immediately
   - Review requests → Reviews directly

RESPONSE FORMAT:
Use function call with:
- agent_type: Selected agent ID
- confidence: Routing confidence (0-1)
- reasoning: Brief explanation"""

    async def process_message(self, message: str, context: Optional[Dict] = None) -> str:
        """Process incoming messages by routing to appropriate specialized agent."""
        logger.info("Processing message through router")
        try:
            # Analyze message and context
            messages = [
                {"role": "system", "content": self._create_system_prompt()},
                {"role": "user", "content": message}
            ]
            
            # Add context if available
            if context and context.get('history'):
                messages[1:1] = context['history'][-3:]  # Only use last 3 messages for context
            
            # Get routing decision
            response = await self.client.chat.completions.create(
                model=os.getenv('GPT_MODEL', 'gpt-4'),
                messages=messages,
                temperature=0.1,  # Lower temperature for more consistent routing
                functions=[{
                    "name": "route_to_agent",
                    "description": "Route the query to a specialized agent",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "agent_type": {
                                "type": "string",
                                "enum": ["product_details", "reviews", "orders"],
                                "description": "The type of agent to route to"
                            },
                            "confidence": {
                                "type": "number",
                                "minimum": 0,
                                "maximum": 1,
                                "description": "Confidence in routing decision"
                            },
                            "reasoning": {
                                "type": "string",
                                "description": "Brief explanation for routing choice"
                            }
                        },
                        "required": ["agent_type", "confidence", "reasoning"]
                    }
                }],
                function_call={"name": "route_to_agent"}
            )
            
            # Parse routing decision
            function_args = json.loads(response.choices[0].message.function_call.arguments)
            agent_type = function_args["agent_type"]
            confidence = function_args["confidence"]
            reasoning = function_args["reasoning"]
            
            logger.info(f"Routing decision: {agent_type} (confidence: {confidence:.2f})")
            logger.info(f"Routing explanation: {reasoning}")
            
            # Get or create agent instance
            if agent_type not in self.agent_instances:
                self.agent_instances[agent_type] = self.available_agents[agent_type]()
                
            # Route to specialized agent
            logger.info(f"Routing message to {agent_type} agent")
            response = await self.agent_instances[agent_type].process_message(message, context)
            
            logger.info("Successfully processed message through router")
            return response
            
        except Exception as e:
            error_msg = f"Error processing message through router: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return "I apologize, but I encountered an error processing your request. Please try again." 