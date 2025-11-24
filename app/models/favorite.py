"""
Favorite Model for SaveMate API
MongoDB/Beanie document model for user favorites
"""

from beanie import Document
from pydantic import Field
from datetime import datetime


class Favorite(Document):
    user_id: str = Field(..., description="User ID")
    deal_id: str = Field(..., description="Deal ID")
    
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When favorited")
    
    class Settings:
        name = "favorites"
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "507f1f77bcf86cd799439011",
                "deal_id": "507f1f77bcf86cd799439012"
            }
        }
    
    def __repr__(self):
        return f"<Favorite user:{self.user_id} deal:{self.deal_id}>"
