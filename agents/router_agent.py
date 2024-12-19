"""Router agent for directing queries to appropriate specialized agents."""
from typing import Dict, List, Optional, Type
from .base_agent import BaseAgent
from .product_details_agent import ProductDetailsAgent
from .reviews_agent import ReviewsAgent
from .orders_agent import OrdersAgent
import logging
import os
import json
import yaml

# Configure logging
logger = logging.getLogger('agents.router')

# Agent class mapping
AGENT_CLASSES = {
    "ProductDetailsAgent": ProductDetailsAgent,
    "ReviewsAgent": ReviewsAgent,
    "OrdersAgent": OrdersAgent
}

class RouterAgent(BaseAgent):
    def __init__(self):
        super().__init__("Router")
        self.agent_config = self._load_agents_from_config()
        self.available_agents = self._initialize_available_agents()
        self.agent_instances: Dict[str, BaseAgent] = {}
        logger.info(f"Initialized {self.__class__.__name__} with {len(self.available_agents)} available agents")
        
    def _load_agents_from_config(self) -> Dict:
        """Load agent configuration from YAML file."""
        try:
            config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'agents_config.yaml')
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            logger.info("Successfully loaded agent configuration")
            return config
        except Exception as e:
            logger.error(f"Error loading agent configuration: {str(e)}", exc_info=True)
            raise

    def _initialize_available_agents(self) -> Dict[str, Type[BaseAgent]]:
        """Initialize available agents from config."""
        available_agents = {}
        for agent_id, config in self.agent_config['agents'].items():
            if config.get('enabled', False):
                agent_class = AGENT_CLASSES.get(config['class'])
                if agent_class:
                    available_agents[agent_id] = agent_class
                else:
                    logger.warning(f"Agent class {config['class']} not found for {agent_id}")
        return available_agents

    def _create_system_prompt(self) -> str:
        """Create the system prompt dynamically from config."""
        # Only include enabled agents in the prompt
        available_agents = []
        for agent_id, config in self.agent_config['agents'].items():
            if agent_id in self.available_agents:  # Only include enabled agents
                agent_section = [
                    f"{len(available_agents) + 1}. {config['name']}",
                    *[f"   - {resp}" for resp in config['responsibilities']],
                    f"   KEYWORDS: {', '.join(config['keywords'])}"
                ]
                available_agents.extend(agent_section)

        prompt = f"""You are a router agent that directs customer queries to specialized agents.

AVAILABLE AGENTS:
{chr(10).join(available_agents)}

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

        return prompt

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
