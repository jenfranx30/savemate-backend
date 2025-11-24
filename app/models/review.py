"""
Review Model for SaveMate API
MongoDB/Beanie document model for deal reviews and ratings
"""

from beanie import Document
from pydantic import Field
from datetime import datetime
from typing import Optional


class Review(Document):
    deal_id: str = Field(..., description="Deal ID being reviewed")
    user_id: str = Field(..., description="User ID of reviewer")
    business_id: str = Field(..., description="Business ID")
    
    rating: int = Field(..., ge=1, le=5, description="Rating 1-5 stars")
    title: Optional[str] = Field(None, max_length=100, description="Review title")
    comment: str = Field(..., min_length=10, max_length=500, description="Review text")
    
    helpful_count: int = Field(default=0, description="Helpful votes")
    
    is_verified_purchase: bool = Field(default=False, description="Verified redemption")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "reviews"
    
    class Config:
        json_schema_extra = {
            "example": {
                "deal_id": "507f1f77bcf86cd799439011",
                "user_id": "507f1f77bcf86cd799439012",
                "business_id": "507f1f77bcf86cd799439013",
                "rating": 5,
                "title": "Amazing pizza deal!",
                "comment": "The pizza was delicious and the discount was great. Will definitely come back!",
                "helpful_count": 12,
                "is_verified_purchase": True
            }
        }
    
    async def increment_helpful(self):
        self.helpful_count += 1
        await self.save()
    
    def __repr__(self):
        return f"<Review {self.rating}★ for deal:{self.deal_id}>"
