from database.data_loader import DataLoader
from database.mongodb_client import MongoDB
import logging

logger = logging.getLogger(__name__)

def init_database():
    """Initialize the database with fresh data."""
    try:
        # Get MongoDB instance
        db = MongoDB()
        
        # Drop existing database to ensure clean state
        logger.info("Dropping existing database...")
        db.client.drop_database(db.db.name)
        logger.info("Database dropped successfully")
        
        # Initialize with fresh data
        logger.info("Loading fresh data...")
        loader = DataLoader()
        loader.load_all_data()
        logger.info("✅ Database initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Error initializing database: {str(e)}")
        raise

if __name__ == "__main__":
    init_database() 