"""
Database connection and initialization
Manages MongoDB connection with Beanie ODM
"""
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.config import settings


class Database:
    """Database connection manager"""
    
    client: AsyncIOMotorClient = None
    
    @classmethod
    async def connect_db(cls):
        """Connect to MongoDB and initialize Beanie"""
        try:
            # Create MongoDB client
            cls.client = AsyncIOMotorClient(settings.MONGODB_URL)
            
            # Get database
            database = cls.client[settings.DATABASE_NAME]
            
            # Initialize Beanie with document models
            # We'll add models later
            await init_beanie(
                database=database,
                document_models=[
                    # Models will be added here in Phase 2
                ]
            )
            
            print(f"✅ Connected to MongoDB database: {settings.DATABASE_NAME}")
            
        except Exception as e:
            print(f"❌ Error connecting to MongoDB: {e}")
            raise
    
    @classmethod
    async def close_db(cls):
        """Close database connection"""
        if cls.client:
            cls.client.close()
            print("✅ MongoDB connection closed")


# Helper functions for FastAPI lifespan events
async def init_db():
    """Initialize database connection"""
    await Database.connect_db()


async def close_db():
    """Close database connection"""
    await Database.close_db()
