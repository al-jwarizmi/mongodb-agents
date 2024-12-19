"""Reviews agent for handling product review queries."""
from typing import Dict, List, Optional
import logging
from .base_agent import BaseAgent
import json
import os
from datetime import datetime

logger = logging.getLogger('agents.reviews')

class ReviewsAgent(BaseAgent):
    def __init__(self):
        super().__init__("Reviews")
        logger.info(f"Initialized {self.__class__.__name__}")
        
    def _register_functions(self):
        """Register available functions for this agent."""
        self.available_functions = {
            'get_product_reviews': self.get_product_reviews,
            'get_review_stats': self.get_review_stats,
            'create_review': self.create_review
        }

    def _create_system_prompt(self) -> str:
        """Create the system prompt for the agent."""
        # Get all reviews from database
        all_reviews = list(self.db.reviews.find({}))
        
        # Format review information by product
        review_info = []
        products_with_reviews = {}
        
        for review in all_reviews:
            product_id = review['product_id']
            if product_id not in products_with_reviews:
                products_with_reviews[product_id] = []
            products_with_reviews[product_id].append(review)
        
        for product_id, reviews in products_with_reviews.items():
            # Get product name
            product = self.db.products.find_one({"id": product_id})
            product_name = product['name'] if product else product_id
            
            review_info.append(f"""
Product: {product_name}
Number of Reviews: {len(reviews)}
Average Rating: {sum(r['rating'] for r in reviews) / len(reviews):.1f}
Sample Reviews:
{chr(10).join(f"- {r['rating']}★: {r['content']}" for r in reviews[:3])}
""")
        
        prompt = f"""You are a Reviews specialist for our mattress company.
Your role is to help customers understand what other customers are saying about our products.

Available Reviews in our Database:
{chr(10).join(review_info)}

When handling customer queries:
1. Use the get_product_reviews function to fetch actual customer reviews
2. Use the get_review_stats function to get statistical information
3. Focus on providing balanced feedback, including both positive and critical reviews
4. Highlight common themes in customer feedback
5. If asked about a product with no reviews, acknowledge this and suggest looking at reviews for similar products

Remember to maintain a helpful and professional tone while providing accurate review information from our database."""
        
        logger.debug(f"Created system prompt with reviews for {len(products_with_reviews)} products")
        return prompt

    @staticmethod
    def get_product_reviews_spec():
        return {
            "name": "get_product_reviews",
            "description": "Get reviews for a specific product",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {
                        "type": "string",
                        "description": "ID or name of the product to get reviews for"
                    },
                    "filter_type": {
                        "type": "string",
                        "enum": ["positive", "negative", "all"],
                        "description": "Type of reviews to retrieve",
                        "default": "all"
                    }
                },
                "required": ["product_id"]
            }
        }

    def get_product_reviews(self, product_id: str, filter_type: str = "all") -> Dict:
        """Get reviews for a specific product."""
        logger.info(f"Getting {filter_type} reviews for product: {product_id}")
        
        # First try exact product ID
        reviews = list(self.db.reviews.find({"product_id": product_id}))
        
        # If no reviews found, try finding product by name
        if not reviews:
            product = self.db.products.find_one({"name": {"$regex": f"^{product_id}", "$options": "i"}})
            if product:
                reviews = list(self.db.reviews.find({"product_id": product["id"]}))
        
        # Filter reviews if needed
        if filter_type == "positive":
            reviews = [r for r in reviews if r.get("rating", 0) >= 4]
        elif filter_type == "negative":
            reviews = [r for r in reviews if r.get("rating", 0) <= 2]
        
        # Format response
        formatted_reviews = []
        for r in reviews:
            formatted_review = {
                "rating": r.get("rating", 0),
                "content": r.get("content", ""),
                "verified_purchase": r.get("verified_purchase", False),
                "customer_id": r.get("customer_id", "anonymous")
            }
            formatted_reviews.append(formatted_review)
        
        response = {
            "product_id": product_id,
            "total_reviews": len(reviews),
            "average_rating": sum(r.get("rating", 0) for r in reviews) / len(reviews) if reviews else 0,
            "filter_type": filter_type,
            "reviews": formatted_reviews
        }
        
        logger.info(f"Found {len(reviews)} {filter_type} reviews for product {product_id}")
        return response

    @staticmethod
    def get_review_stats_spec():
        return {
            "name": "get_review_stats",
            "description": "Get statistical information about product reviews",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {
                        "type": "string",
                        "description": "ID or name of the product to get statistics for"
                    }
                },
                "required": ["product_id"]
            }
        }

    def get_review_stats(self, product_id: str) -> Dict:
        """Get statistical information about product reviews."""
        logger.info(f"Getting review statistics for product: {product_id}")
        
        # Get all reviews for the product
        reviews = list(self.db.reviews.find({"product_id": product_id}))
        
        if not reviews:
            # Try finding product by name
            product = self.db.products.find_one({"name": {"$regex": f"^{product_id}", "$options": "i"}})
            if product:
                reviews = list(self.db.reviews.find({"product_id": product["id"]}))
        
        # Calculate statistics
        total_reviews = len(reviews)
        if total_reviews == 0:
            return {
                "product_id": product_id,
                "total_reviews": 0,
                "message": "No reviews found for this product"
            }
        
        ratings = [r.get("rating", 0) for r in reviews]
        stats = {
            "product_id": product_id,
            "total_reviews": total_reviews,
            "average_rating": sum(ratings) / total_reviews,
            "rating_distribution": {
                "5_star": len([r for r in ratings if r == 5]),
                "4_star": len([r for r in ratings if r == 4]),
                "3_star": len([r for r in ratings if r == 3]),
                "2_star": len([r for r in ratings if r == 2]),
                "1_star": len([r for r in ratings if r == 1])
            },
            "verified_purchases": len([r for r in reviews if r.get("verified_purchase", False)])
        }
        
        logger.info(f"Calculated statistics for {total_reviews} reviews of product {product_id}")
        return stats

    @staticmethod
    def create_review_spec():
        return {
            "name": "create_review",
            "description": "Create a new review for a product",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {
                        "type": "string",
                        "description": "ID of the product being reviewed"
                    },
                    "rating": {
                        "type": "integer",
                        "description": "Rating from 1 to 5 stars",
                        "minimum": 1,
                        "maximum": 5
                    },
                    "content": {
                        "type": "string",
                        "description": "Review text content"
                    }
                },
                "required": ["product_id", "rating", "content"]
            }
        }

    def create_review(self, product_id: str, rating: int, content: str) -> Dict:
        """Create a new review for a product."""
        logger.info(f"Creating review for product {product_id} with rating {rating}")
        
        try:
            # Validate rating first
            if not 1 <= rating <= 5:
                raise ValueError("Rating must be between 1 and 5")
            
            # Validate product exists
            product = self.db.products.find_one({"id": product_id})
            if not product:
                # Try finding by name
                product = self.db.products.find_one({"name": {"$regex": f"^{product_id}", "$options": "i"}})
                if not product:
                    raise ValueError(f"Product not found: {product_id}")
                product_id = product["id"]
            
            # Create review document
            review = {
                "product_id": product_id,
                "rating": rating,
                "content": content,
                "created_at": datetime.now().isoformat(),  # Store as ISO string
                "verified_purchase": True  # For the code challenge, we'll assume all reviews are verified
            }
            
            # Save to database
            result = self.db.reviews.insert_one(review)
            
            if not result.inserted_id:
                raise Exception("Failed to create review")
            
            response = {
                "success": True,
                "product_id": product_id,
                "rating": rating,
                "content": content,
                "message": "Review submitted successfully"
            }
            
            logger.info(f"Successfully created review for product {product_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error creating review: {str(e)}", exc_info=True)
            raise

    async def process_message(self, message: str, context: Optional[Dict] = None) -> str:
        """Process an incoming message and return a response."""
        try:
            logger.debug(f"Processing message in ReviewsAgent: {message}")
            
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
                    self.get_product_reviews_spec(),
                    self.get_review_stats_spec(),
                    self.create_review_spec()
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
                if function_name == "get_product_reviews":
                    result = self.get_product_reviews(**function_args)
                elif function_name == "get_review_stats":
                    result = self.get_review_stats(**function_args)
                elif function_name == "create_review":
                    result = self.create_review(**function_args)
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