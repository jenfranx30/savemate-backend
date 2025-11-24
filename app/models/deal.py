"""
Deal Model for SaveMate API
MongoDB/Beanie document model for deals and offers
"""

from beanie import Document
from pydantic import Field, HttpUrl
from datetime import datetime
from typing import Optional, List
from enum import Enum


class DealCategory(str, Enum):
    FOOD = "food"
    DRINKS = "drinks"
    SHOPPING = "shopping"
    ENTERTAINMENT = "entertainment"
    HEALTH = "health"
    BEAUTY = "beauty"
    SERVICES = "services"
    TRAVEL = "travel"
    ELECTRONICS = "electronics"
    OTHER = "other"


class DealStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    PENDING = "pending"
    INACTIVE = "inactive"


class Deal(Document):
    title: str = Field(..., min_length=5, max_length=200, description="Deal title")
    description: str = Field(..., min_length=20, max_length=2000, description="Detailed description")

    original_price: float = Field(..., gt=0, description="Original price in PLN")
    discounted_price: float = Field(..., gt=0, description="Discounted price in PLN")
    discount_percentage: Optional[int] = Field(None, ge=0, le=100, description="Discount percentage")

    category: DealCategory = Field(..., description="Deal category")
    tags: List[str] = Field(default_factory=list, description="Search tags")

    business_id: str = Field(..., description="ID of business offering the deal")
    business_name: str = Field(..., description="Name of the business")

    location: dict = Field(..., description="Business location")

    start_date: datetime = Field(default_factory=datetime.utcnow, description="When deal starts")
    end_date: datetime = Field(..., description="When deal expires")

    status: DealStatus = Field(default=DealStatus.ACTIVE, description="Deal status")
    is_featured: bool = Field(default=False, description="Featured deal")

    image_url: Optional[HttpUrl] = Field(None, description="Deal image URL")
    additional_images: List[HttpUrl] = Field(default_factory=list, description="Additional images")

    views_count: int = Field(default=0, description="Number of views")
    saves_count: int = Field(default=0, description="Number of saves/favorites")

    terms: Optional[str] = Field(None, max_length=1000, description="Terms and conditions")
    quantity_available: Optional[int] = Field(None, gt=0, description="Available quantity")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str = Field(..., description="User ID who created this deal")

    class Settings:
        name = "deals"

    class Config:
        json_schema_extra = {
            "example": {
                "title": "50% Off Large Pizza",
                "description": "Get half off any large pizza with 3+ toppings. Valid for dine-in and takeout.",
                "original_price": 39.99,
                "discounted_price": 19.99,
                "discount_percentage": 50,
                "category": "food",
                "tags": ["pizza", "italian", "dinner"],
                "business_id": "507f1f77bcf86cd799439011",
                "business_name": "Mario's Pizzeria",
                "location": {
                    "address": "ul. Marszałkowska 123",
                    "city": "Warsaw",
                    "postal_code": "00-001",
                    "country": "Poland"
                },
                "end_date": "2025-12-31T23:59:59",
                "image_url": "https://example.com/pizza.jpg",
                "terms": "Cannot be combined with other offers. One per customer.",
                "quantity_available": 100
            }
        }

    def calculate_discount_percentage(self):
        if self.original_price > 0:
            discount = ((self.original_price - self.discounted_price) / self.original_price) * 100
            self.discount_percentage = round(discount)

    def is_expired(self) -> bool:
        return datetime.utcnow() > self.end_date

    def is_valid(self) -> bool:
        now = datetime.utcnow()
        return (
            self.status == DealStatus.ACTIVE and
            self.start_date <= now <= self.end_date
        )

    async def increment_views(self):
        self.views_count += 1
        await self.save()

    async def increment_saves(self):
        self.saves_count += 1
        await self.save()

    def __repr__(self):
        return f"<Deal {self.title} - {self.discount_percentage}% off>"