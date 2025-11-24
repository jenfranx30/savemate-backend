"""
Review Schemas for SaveMate API
Pydantic models for review-related requests and responses
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class ReviewCreate(BaseModel):
    deal_id: str = Field(..., description="Deal ID")
    rating: int = Field(..., ge=1, le=5, description="Rating 1-5")
    title: Optional[str] = Field(None, max_length=100)
    comment: str = Field(..., min_length=10, max_length=500)
    
    class Config:
        json_schema_extra = {
            "example": {
                "deal_id": "507f1f77bcf86cd799439011",
                "rating": 5,
                "title": "Amazing deal!",
                "comment": "Great pizza and excellent service. Highly recommended!"
            }
        }


class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5)
    title: Optional[str] = Field(None, max_length=100)
    comment: Optional[str] = Field(None, min_length=10, max_length=500)


class ReviewResponse(BaseModel):
    id: str
    deal_id: str
    user_id: str
    business_id: str
    rating: int
    title: Optional[str]
    comment: str
    helpful_count: int
    is_verified_purchase: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "deal_id": "507f1f77bcf86cd799439012",
                "user_id": "507f1f77bcf86cd799439013",
                "business_id": "507f1f77bcf86cd799439014",
                "rating": 5,
                "title": "Amazing deal!",
                "comment": "Great pizza and excellent service.",
                "helpful_count": 10,
                "is_verified_purchase": True,
                "created_at": "2025-11-24T10:00:00",
                "updated_at": "2025-11-24T10:00:00"
            }
        }


class ReviewListResponse(BaseModel):
    reviews: List[ReviewResponse]
    total: int
    average_rating: float


class ReviewDeleteResponse(BaseModel):
    message: str
    review_id: str


class ReviewHelpfulResponse(BaseModel):
    message: str
    helpful_count: int
