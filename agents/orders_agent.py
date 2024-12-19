"""Orders agent for handling purchase and order status queries."""
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
from .base_agent import BaseAgent
import json
import os

logger = logging.getLogger('agents.orders')

class OrdersAgent(BaseAgent):
    def __init__(self):
        super().__init__("Orders")
        logger.info(f"Initialized {self.__class__.__name__}")
        
    def _register_functions(self):
        """Register available functions for this agent."""
        self.available_functions = {
            'create_order': self.create_order,
            'get_order_status': self.get_order_status
        }

    def _create_system_prompt(self) -> str:
        """Create the system prompt for the agent."""
        # Get available products for pricing
        products = list(self.db.products.find({}))
        
        # Format product information
        product_info = []
        for p in products:
            product_info.append(f"""
Product: {p['name']}
ID: {p['id']}
Price: ${p['price']}
Available Sizes: {', '.join(p['available_sizes'])}
""")
        
        prompt = f"""You are Frodo, a friendly and efficient order specialist.
Your role is to help customers place orders for mattresses and check order status.

Available Products:
{chr(10).join(product_info)}

Your responsibilities:
1. Order Creation Process:
   a. Initial Order Intent:
      - Confirm product and size selection
      - Provide pricing information
   b. Collect Information:
      - Ask for delivery address
      - Ask for payment method (credit card, debit card, or PayPal)
   c. Complete Order:
      - Create order with order ID
      - Provide order confirmation with delivery estimate

2. Order Status:
   - Check and provide order status
   - Provide estimated delivery dates
   - Answer basic shipping questions

Communication Style:
- Be friendly and efficient
- Keep responses concise
- Confirm details clearly
- Guide customer through each step

Example Conversations:

Customer: "I'll take the Ultra Comfort in Queen size."
Frodo: "Great choice! I'll help you place that order for a Queen size Ultra Comfort Mattress. The price is $1,299, and we're currently offering free delivery. Could you please provide your delivery address?"

Customer: "123 Main St, Springfield, MA"
Frodo: "Thank you! And what would be your preferred payment method - credit card, debit card, or PayPal?"

Customer: "Credit card please"
Frodo: "Perfect! I've processed your order. Your order number is #UC789321. You can expect delivery within 5-7 business days. We'll send you a confirmation email with tracking details shortly. Is there anything else you'd like to know about your order?"

Remember to:
1. Always confirm the product and size
2. Provide clear pricing information
3. Ask for delivery address
4. Ask for payment method
5. Generate unique order IDs
6. Give delivery estimates (5-7 business days)"""
        
        return prompt

    @staticmethod
    def create_order_spec():
        return {
            "name": "create_order",
            "description": "Create a new order for a product",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {
                        "type": "string",
                        "description": "ID of the product being ordered"
                    },
                    "size": {
                        "type": "string",
                        "description": "Size of the mattress",
                        "enum": ["Twin", "Twin XL", "Full", "Queen", "King", "California King"]
                    },
                    "quantity": {
                        "type": "integer",
                        "description": "Number of items to order",
                        "default": 1
                    },
                    "delivery_address": {
                        "type": "string",
                        "description": "Customer's delivery address"
                    },
                    "payment_method": {
                        "type": "string",
                        "description": "Customer's payment method",
                        "enum": ["credit_card", "debit_card", "paypal"]
                    }
                },
                "required": ["product_id", "size", "delivery_address", "payment_method"]
            }
        }

    def create_order(self, product_id: str, size: str, delivery_address: str, payment_method: str, quantity: int = 1) -> Dict:
        """Create a new order in the system."""
        logger.info(f"Creating order for product {product_id}, size {size}, quantity {quantity}")
        
        try:
            # Validate product exists
            product = self.db.products.find_one({"id": product_id})
            if not product:
                raise ValueError(f"Product not found: {product_id}")
            
            # Validate size is available
            if size not in product["available_sizes"]:
                raise ValueError(f"Size {size} not available for {product['name']}")
            
            # Create order
            order = {
                "order_id": self._generate_order_id(),
                "product_id": product_id,
                "product_name": product["name"],
                "size": size,
                "quantity": quantity,
                "price": product["price"],
                "total": product["price"] * quantity,
                "status": "confirmed",
                "delivery_address": delivery_address,
                "payment_method": payment_method,
                "created_at": datetime.utcnow()
            }
            
            # Save to database
            result = self.db.orders.insert_one(order)
            
            if not result.inserted_id:
                raise Exception("Failed to create order")
            
            response = {
                "success": True,
                "order_id": order["order_id"],
                "total": order["total"],
                "status": "confirmed",
                "delivery_address": delivery_address,
                "payment_method": payment_method,
                "estimated_delivery": "5-7 business days"
            }
            
            logger.info(f"Successfully created order {order['order_id']}")
            return response
            
        except Exception as e:
            logger.error(f"Error creating order: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def get_order_status_spec():
        return {
            "name": "get_order_status",
            "description": "Get status information for an order",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "ID of the order to check"
                    }
                },
                "required": ["order_id"]
            }
        }

    def get_order_status(self, order_id: str) -> Dict:
        """Get status information for an order."""
        logger.info(f"Checking status for order: {order_id}")
        
        try:
            # Find order
            order = self.db.orders.find_one({"order_id": order_id})
            if not order:
                raise ValueError(f"Order not found: {order_id}")
            
            # Format response
            response = {
                "order_id": order["order_id"],
                "product": order["product_name"],
                "size": order["size"],
                "quantity": order["quantity"],
                "total": order["total"],
                "status": order["status"],
                "created_at": order["created_at"].isoformat(),
                "estimated_delivery": "5-7 business days"
            }
            
            logger.info(f"Successfully retrieved status for order {order_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error getting order status: {str(e)}", exc_info=True)
            raise

    def _generate_order_id(self) -> str:
        """Generate a unique order ID."""
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        return f"UC{timestamp[-6:]}"

    async def process_message(self, message: str, context: Optional[Dict] = None) -> str:
        """Process an incoming message and return a response."""
        try:
            logger.debug(f"Processing message in OrdersAgent: {message}")
            
            # Create messages for OpenAI
            messages = [
                {"role": "system", "content": self._create_system_prompt()},
                {"role": "user", "content": message}
            ]
            
            # Add context if provided
            if context and context.get('history'):
                messages[1:1] = context['history']
            
            # Get response from OpenAI with function calling
            response = await self.client.chat.completions.create(
                model=os.getenv('GPT_MODEL', 'gpt-4'),
                messages=messages,
                functions=[
                    self.create_order_spec(),
                    self.get_order_status_spec()
                ],
                temperature=float(os.getenv('TEMPERATURE', '0.7'))
            )
            
            response_message = response.choices[0].message
            
            # Handle function calling
            if response_message.function_call:
                logger.debug(f"Function call requested: {response_message.function_call.name}")
                
                # Parse function arguments
                function_name = response_message.function_call.name
                function_args = json.loads(response_message.function_call.arguments)
                
                # Execute function
                if function_name == "create_order":
                    result = self.create_order(**function_args)
                elif function_name == "get_order_status":
                    result = self.get_order_status(**function_args)
                else:
                    raise ValueError(f"Unknown function: {function_name}")
                
                # Add function response to conversation
                messages.append({
                    "role": "assistant",
                    "content": None,
                    "function_call": {
                        "name": function_name,
                        "arguments": json.dumps(function_args)
                    }
                })
                messages.append({
                    "role": "function",
                    "name": function_name,
                    "content": json.dumps(result)
                })
                
                # Get final response from OpenAI
                logger.debug("Getting final response from OpenAI with function results")
                final_response = await self.client.chat.completions.create(
                    model=os.getenv('GPT_MODEL', 'gpt-4'),
                    messages=messages,
                    temperature=float(os.getenv('TEMPERATURE', '0.7'))
                )
                
                return final_response.choices[0].message.content
            
            return response_message.content
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}", exc_info=True)
            return f"I apologize, but I encountered an error processing your request: {str(e)}" 