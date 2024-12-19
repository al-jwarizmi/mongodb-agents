from typing import Dict, Optional, List
from .base_agent import BaseAgent
import re
import logging
import json
from datetime import datetime
import os

# Configure logging
logger = logging.getLogger('agents.product_details')

class ProductDetailsAgent(BaseAgent):
    def __init__(self):
        super().__init__("Product Details")
        # Cache of available products
        self._available_products = None
        logger.info(f"Initialized {self.__class__.__name__}")
        
    def _register_functions(self):
        """Register available functions for this agent."""
        self.available_functions = {
            'get_product_details': self.get_product_details,
            'compare_products': self.compare_products
        }
        
    def _get_available_products(self) -> List[Dict]:
        """Get list of all available products with their names and IDs."""
        if self._available_products is None:
            logger.debug("Fetching available products from database")
            products = list(self.db.products.find({}, {"id": 1, "name": 1, "_id": 0}))
            self._available_products = [{
                "id": p["id"],
                "name": p["name"],
                "name_normalized": p["name"].lower()
            } for p in products]
            logger.info(f"Cached {len(self._available_products)} products")
            logger.debug(f"Available products: {json.dumps([p['name'] for p in self._available_products])}")
        return self._available_products

    def _find_matching_product(self, product_reference: str) -> Optional[str]:
        """Find a matching product ID from a user's reference to a product."""
        if not product_reference:
            logger.warning("Empty product reference provided")
            return None
            
        # Normalize the reference
        reference_normalized = product_reference.lower().strip()
        logger.debug(f"Finding match for normalized reference: '{reference_normalized}'")
        
        # Get available products
        available_products = self._get_available_products()
        
        # Try exact matches first
        logger.debug("Attempting exact matches")
        for product in available_products:
            # Match against ID
            if reference_normalized == product["id"]:
                logger.info(f"Found exact ID match: {product['id']}")
                return product["id"]
            # Match against full name
            if reference_normalized == product["name_normalized"]:
                logger.info(f"Found exact name match: {product['name']} ({product['id']})")
                return product["id"]
            
        # Try partial matches
        logger.debug("Attempting partial matches")
        # Convert reference to kebab case (e.g., "Ultra Comfort" -> "ultra-comfort")
        reference_kebab = reference_normalized.replace(" ", "-").replace("_", "-")
        reference_without_mattress = reference_kebab.replace("-mattress", "")
        logger.debug(f"Reference in kebab case: '{reference_kebab}'")
        logger.debug(f"Reference without 'mattress': '{reference_without_mattress}'")
        
        for product in available_products:
            # Try matching against ID parts
            if reference_without_mattress in product["id"]:
                logger.info(f"Found partial ID match: {product['name']} ({product['id']}) for reference '{product_reference}'")
                return product["id"]
            
            # Try matching against name parts
            product_name_parts = set(product["name_normalized"].split())
            reference_parts = set(reference_normalized.split())
            # If more than 50% of the words match, consider it a match
            matching_parts = product_name_parts.intersection(reference_parts)
            if len(matching_parts) >= len(reference_parts) / 2:
                logger.info(f"Found fuzzy name match: {product['name']} ({product['id']}) for reference '{product_reference}'")
                return product["id"]
            
        logger.warning(f"No matching product found for reference: '{product_reference}'")
        return None

    @staticmethod
    def get_product_details_spec():
        return {
            "name": "get_product_details",
            "description": "Get detailed information about a specific mattress product",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {
                        "type": "string",
                        "description": "Name or ID of the product to retrieve details for"
                    }
                },
                "required": ["product_id"]
            }
        }

    def get_product_details(self, product_id: str) -> Dict:
        """Get details for a specific product."""
        logger.info(f"Getting details for product: {product_id}")
        
        try:
            # Find product
            product = self.db.products.find_one({"id": product_id})
            if not product:
                # Try finding by name
                product = self.db.products.find_one({"name": {"$regex": f"^{product_id}", "$options": "i"}})
                if not product:
                    raise ValueError(f"Product not found: {product_id}")
            
            # Clean up the product data for serialization
            cleaned_product = {
                "id": product["id"],
                "name": product["name"],
                "price": product["price"],
                "type": product["type"],
                "construction_layers": product["construction_layers"],
                "key_features": product["key_features"],
                "best_for": product["best_for"],
                "available_sizes": product["available_sizes"],
                "warranty": product["warranty"],
                "trial_period": product["trial_period"]
            }
            
            # Convert datetime to string if present
            if "created_at" in product:
                cleaned_product["created_at"] = product["created_at"].isoformat()
            
            # Log the cleaned data
            logger.debug(f"Product details: {cleaned_product}")
            return cleaned_product
            
        except Exception as e:
            logger.error(f"Error getting product details: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def compare_products_spec():
        return {
            "name": "compare_products",
            "description": "Compare multiple mattress products",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_ids": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "Names or IDs of products to compare",
                        "minItems": 1
                    }
                },
                "required": ["product_ids"]
            }
        }

    def compare_products(self, product_ids: List[str]) -> Dict:
        """Compare multiple products side by side."""
        logger.info(f"Comparing products: {product_ids}")
        products = []
        not_found = []
        
        for pid in product_ids:
            logger.debug(f"Processing product reference: '{pid}'")
            actual_product_id = self._find_matching_product(pid)
            if actual_product_id:
                logger.debug(f"Found matching product ID: {actual_product_id}")
                product = self.db.products.find_one({"id": actual_product_id})
                if product:
                    formatted_product = {
                        "id": product["id"],
                        "name": product["name"],
                        "price": product["price"],
                        "type": product["type"],
                        "construction_layers": product["construction_layers"],
                        "key_features": product["key_features"],
                        "best_for": product["best_for"],
                        "available_sizes": product["available_sizes"],
                        "warranty": product["warranty"],
                        "trial_period": product["trial_period"]
                    }
                    products.append(formatted_product)
                    logger.info(f"Added product to comparison: {formatted_product['name']} ({formatted_product['id']})")
                else:
                    logger.error(f"Product data not found for ID: {actual_product_id}")
            else:
                not_found.append(pid)
                logger.warning(f"No matching product found for: '{pid}'")
        
        response = {
            "total_products": len(products),
            "products": products
        }
        
        if not_found:
            available_names = [p["name"] for p in self._get_available_products()]
            response["not_found"] = {
                "products": not_found,
                "available_products": available_names
            }
            logger.warning(f"Some products not found: {not_found}")
            logger.debug(f"Available products: {available_names}")
            
        logger.info(f"Comparison complete. Found {len(products)} products, {len(not_found)} not found")
        return response

    async def process_message(self, message: str, context: Optional[Dict] = None) -> str:
        """Process an incoming message and return a response."""
        try:
            logger.debug(f"Processing message in ProductDetailsAgent: {message}")
            
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
                    self.get_product_details_spec(),
                    self.compare_products_spec()
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
                if function_name == "get_product_details":
                    result = self.get_product_details(function_args["product_id"])
                elif function_name == "compare_products":
                    result = self.compare_products(function_args["product_ids"])
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

    def _create_system_prompt(self) -> str:
        """Create the system prompt for the agent."""
        # Get all products from database
        products = list(self.db.products.find({}))
        
        # Format product information
        product_info = []
        for p in products:
            product_info.append(f"""
Product ID: {p['id']}
Name: {p['name']}
Type: {p['type']}
Price: ${p['price']}
Key Features: {', '.join(p['key_features'][:3])}
Best For: {', '.join(p['best_for'])}
""")
        
        # Create the prompt with product catalog
        prompt = f"""You are a friendly and knowledgeable mattress expert named Frodo.
Your role is to help customers understand our products and make informed decisions.

Available Products in our Catalog:
{chr(10).join(product_info)}

Communication Style:
1. Be conversational and friendly, like chatting with a knowledgeable friend
2. Keep responses concise but informative
3. Use simple language and avoid technical jargon
4. Break down complex comparisons into clear points
5. Focus on the most relevant features for the customer's needs

When comparing products:
1. Start with a brief overview of key differences
2. Highlight the main strengths of each mattress
3. Focus on practical benefits rather than technical specifications
4. Explain who each mattress is best suited for
5. End with an open question to understand the customer's preferences better

When handling queries:
1. If a customer asks about a product not in our catalog:
   - Politely acknowledge that we don't carry it
   - Suggest similar alternatives from our lineup
2. For product comparisons:
   - Focus on key differences that matter most
   - Explain benefits in practical terms
3. Always maintain a helpful and friendly tone

Example response style:
"I'd be happy to help you compare the Ultra Comfort and Dream Sleep mattresses. The Ultra Comfort features a 12-inch hybrid design with memory foam and pocket coils, while the Dream Sleep is a 10-inch all-foam mattress. The Ultra Comfort offers better temperature regulation and edge support due to its coil system, while the Dream Sleep excels in motion isolation and is generally better for side sleepers. Would you like me to break down any specific features in more detail?"

Remember to keep responses friendly, concise, and focused on helping customers find their perfect mattress."""
        
        logger.debug(f"Created system prompt with {len(products)} products")
        return prompt