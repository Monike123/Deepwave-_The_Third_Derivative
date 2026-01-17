"""
MongoDB Connection Manager
Provides async MongoDB connection using Motor driver
"""
import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ServerSelectionTimeoutError

logger = logging.getLogger(__name__)


class Database:
    """MongoDB connection manager with connection pooling"""
    
    client: AsyncIOMotorClient = None
    db = None
    
    # Collection names
    UPLOADS = "uploads"
    ANALYSIS_RESULTS = "analysis_results"
    SESSIONS = "sessions"
    ANALYTICS = "analytics"
    USERS = "users"
    
    @classmethod
    async def connect(cls):
        """Connect to MongoDB"""
        try:
            # Get MongoDB URI from environment or use local default
            mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
            db_name = os.getenv("MONGODB_DB_NAME", "deepway")
            
            logger.info(f"Connecting to MongoDB at {mongodb_uri[:30]}...")
            
            cls.client = AsyncIOMotorClient(
                mongodb_uri,
                serverSelectionTimeoutMS=5000,
                maxPoolSize=50
            )
            
            # Verify connection
            await cls.client.admin.command('ping')
            
            cls.db = cls.client[db_name]
            
            # Create indexes for performance
            await cls._create_indexes()
            
            logger.info(f"✓ Connected to MongoDB database: {db_name}")
            return True
            
        except ServerSelectionTimeoutError:
            logger.warning("MongoDB not available - running without database storage")
            cls.client = None
            cls.db = None
            return False
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            cls.client = None
            cls.db = None
            return False
    
    @classmethod
    async def disconnect(cls):
        """Close MongoDB connection"""
        if cls.client:
            cls.client.close()
            logger.info("MongoDB connection closed")
    
    @classmethod
    async def _create_indexes(cls):
        """Create database indexes for performance"""
        try:
            # Uploads collection indexes
            await cls.db[cls.UPLOADS].create_index("session_id")
            await cls.db[cls.UPLOADS].create_index("uploaded_at")
            await cls.db[cls.UPLOADS].create_index("file_hash", unique=True, sparse=True)
            
            # Analysis results indexes
            await cls.db[cls.ANALYSIS_RESULTS].create_index("upload_id")
            await cls.db[cls.ANALYSIS_RESULTS].create_index("analyzed_at")
            await cls.db[cls.ANALYSIS_RESULTS].create_index("classification")
            
            # Sessions indexes
            await cls.db[cls.SESSIONS].create_index("session_token", unique=True)
            await cls.db[cls.SESSIONS].create_index("started_at")
            
            # Analytics indexes
            await cls.db[cls.ANALYTICS].create_index("session_id")
            await cls.db[cls.ANALYTICS].create_index("event_type")
            await cls.db[cls.ANALYTICS].create_index("timestamp")
            
            logger.info("Database indexes created")
        except Exception as e:
            logger.warning(f"Failed to create some indexes: {e}")
    
    @classmethod
    def is_connected(cls) -> bool:
        """Check if database is connected"""
        return cls.db is not None
    
    @classmethod
    def get_collection(cls, name: str):
        """Get a collection by name"""
        if cls.db is None:
            return None
        return cls.db[name]


# Convenience instance
database = Database()
