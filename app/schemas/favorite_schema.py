"""
Favorite Schemas for SaveMate API
Pydantic models for favorite-related requests and responses
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List


class FavoriteCreate(BaseModel):
    deal_id: str = Field(..., description="Deal ID to favorite")
    
    class Config:
        json_schema_extra = {
            "example": {
                "deal_id": "507f1f77bcf86cd799439011"
            }
        }


class FavoriteResponse(BaseModel):
    id: str
    user_id: str
    deal_id: str
    created_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "user_id": "507f1f77bcf86cd799439012",
                "deal_id": "507f1f77bcf86cd799439013",
                "created_at": "2025-11-24T10:00:00"
            }
        }


class FavoriteWithDeal(BaseModel):
    id: str
    user_id: str
    deal_id: str
    created_at: datetime
    deal: dict
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "user_id": "507f1f77bcf86cd799439012",
                "deal_id": "507f1f77bcf86cd799439013",
                "created_at": "2025-11-24T10:00:00",
                "deal": {
                    "title": "50% Off Pizza",
                    "discounted_price": 19.99
                }
            }
        }


class FavoriteListResponse(BaseModel):
    favorites: List[FavoriteWithDeal]
    total: int


class FavoriteDeleteResponse(BaseModel):
    message: str
    deal_id: str


class FavoriteCheckResponse(BaseModel):
    is_favorited: bool
    deal_id: str
