"""
Business Model for SaveMate API
MongoDB/Beanie document model for business profiles
"""

from beanie import Document
from pydantic import Field, EmailStr, HttpUrl, BaseModel
from datetime import datetime
from typing import Optional, List
from enum import Enum


class BusinessStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CLOSED = "closed"


class BusinessCategory(str, Enum):
    RESTAURANT = "restaurant"
    CAFE = "cafe"
    RETAIL = "retail"
    GROCERY = "grocery"
    BEAUTY = "beauty"
    FITNESS = "fitness"
    ENTERTAINMENT = "entertainment"
    SERVICES = "services"
    HEALTHCARE = "healthcare"
    OTHER = "other"


class OperatingHours(BaseModel):
    day: str
    open_time: Optional[str] = None
    close_time: Optional[str] = None
    is_closed: bool = False


class Business(Document):
    owner_id: str = Field(..., description="User ID of business owner")

    business_name: str = Field(..., min_length=2, max_length=200, description="Business name")
    description: str = Field(..., min_length=20, max_length=1000, description="Business description")
    category: BusinessCategory = Field(..., description="Business category")

    email: EmailStr = Field(..., description="Business contact email")
    phone: str = Field(..., min_length=9, max_length=20, description="Business phone number")
    website: Optional[HttpUrl] = Field(None, description="Business website")

    location: dict = Field(..., description="Business location")

    logo_url: Optional[HttpUrl] = Field(None, description="Business logo URL")
    cover_image_url: Optional[HttpUrl] = Field(None, description="Cover image URL")
    images: List[HttpUrl] = Field(default_factory=list, description="Additional images")

    operating_hours: List[OperatingHours] = Field(default_factory=list, description="Weekly operating hours")

    status: BusinessStatus = Field(default=BusinessStatus.PENDING, description="Business status")
    is_verified: bool = Field(default=False, description="Verification status")

    rating_average: float = Field(default=0.0, ge=0, le=5, description="Average rating")
    rating_count: int = Field(default=0, description="Number of ratings")

    total_deals: int = Field(default=0, description="Total deals created")
    active_deals: int = Field(default=0, description="Currently active deals")

    followers_count: int = Field(default=0, description="Number of followers")

    tags: List[str] = Field(default_factory=list, description="Search tags")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "businesses"

    async def increment_deals(self):
        self.total_deals += 1
        self.active_deals += 1
        await self.save()

    async def decrement_active_deals(self):
        if self.active_deals > 0:
            self.active_deals -= 1
        await self.save()

    async def update_rating(self, new_rating: float):
        total = (self.rating_average * self.rating_count) + new_rating
        self.rating_count += 1
        self.rating_average = round(total / self.rating_count, 2)
        await self.save()

    def __repr__(self):
        return f"<Business {self.business_name} - {self.category}>"