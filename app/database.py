"""
Database connection and initialization
Manages MongoDB connection with Beanie ODM
"""
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.config import settings

from app.models.user import User
from app.models.deal import Deal
from app.models.business import Business
from app.models.category import Category
from app.models.favorite import Favorite
from app.models.review import Review


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
            await init_beanie(
                database=database,
                document_models=[
                    User,
                    Deal,
                    Business,
                    Category,
                    Favorite,
                    Review,
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