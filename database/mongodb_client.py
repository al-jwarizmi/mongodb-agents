"""MongoDB client for the Sleep Better customer support system."""
from typing import Dict, List, Optional
import os
from datetime import datetime
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get MongoDB connection string from environment variable
MONGODB_CONNECTION_STRING = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
DATABASE_NAME = os.getenv('DB_NAME', 'sleep_better')

# Singleton instances
_db_instance: Optional['MongoDB'] = None

class MongoDB:
    def __init__(self):
        self.client = MongoClient(MONGODB_CONNECTION_STRING)
        self.db: Database = self.client[DATABASE_NAME]
        
        # Initialize collections
        self.orders: Collection = self.db.orders
        self.products: Collection = self.db.products
        self.reviews: Collection = self.db.reviews

    def create_order(self, order_data: Dict) -> str:
        """Create a new order in the database."""
        order_data['created_at'] = datetime.utcnow()
        order_data['status'] = 'pending'
        result = self.orders.insert_one(order_data)
        return str(result.inserted_id)

    def get_order(self, order_id: str) -> Optional[Dict]:
        """Retrieve an order by its ID."""
        return self.orders.find_one({'_id': order_id})

    def update_order_status(self, order_id: str, status: str) -> bool:
        """Update the status of an order."""
        result = self.orders.update_one(
            {'_id': order_id},
            {'$set': {'status': status, 'updated_at': datetime.utcnow()}}
        )
        return result.modified_count > 0

    def get_customer_orders(self, customer_id: str) -> List[Dict]:
        """Retrieve all orders for a specific customer."""
        return list(self.orders.find({'customer_id': customer_id}))

    def add_review(self, review_data: Dict) -> str:
        """Add a new review."""
        review_data['created_at'] = datetime.utcnow()
        result = self.reviews.insert_one(review_data)
        return str(result.inserted_id)

    def get_product_reviews(self, product_id: str) -> List[Dict]:
        """Get all reviews for a specific product."""
        return list(self.reviews.find({'product_id': product_id}))

    def has_customer_purchased_product(self, customer_id: str, product_id: str) -> bool:
        """Check if a customer has purchased a specific product."""
        return self.orders.find_one({
            'customer_id': customer_id,
            'product_id': product_id,
            'status': 'completed'
        }) is not None

def get_database() -> Database:
    """Get a MongoDB database instance."""
    global _db_instance
    
    if _db_instance is None:
        _db_instance = MongoDB()
    
    return _db_instance.db

def close_connections():
    """Close all database connections."""
    global _db_instance
    
    if _db_instance is not None:
        _db_instance.client.close()
        _db_instance = None