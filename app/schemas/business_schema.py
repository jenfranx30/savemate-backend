"""
Business Schemas for SaveMate API
Pydantic models for business-related requests and responses
"""

from pydantic import BaseModel, Field, EmailStr, HttpUrl, validator
from datetime import datetime
from typing import Optional, List
from app.models.business import BusinessCategory, BusinessStatus, OperatingHours


class LocationSchema(BaseModel):
    address: str = Field(..., min_length=5)
    city: str = Field(..., min_length=2)
    postal_code: Optional[str] = None
    country: str = Field(default="Poland")
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class BusinessCreate(BaseModel):
    business_name: str = Field(..., min_length=2, max_length=200)
    description: str = Field(..., min_length=20, max_length=1000)
    category: BusinessCategory
    email: EmailStr
    phone: str = Field(..., min_length=9, max_length=20)
    website: Optional[HttpUrl] = None
    location: LocationSchema
    logo_url: Optional[HttpUrl] = None
    cover_image_url: Optional[HttpUrl] = None
    images: List[HttpUrl] = Field(default_factory=list, max_items=10)
    operating_hours: List[OperatingHours] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list, max_items=10)
    
    class Config:
        json_schema_extra = {
            "example": {
                "business_name": "Mario's Pizzeria",
                "description": "Authentic Italian pizza in Warsaw. Family-owned since 1995.",
                "category": "restaurant",
                "email": "info@mariospizza.pl",
                "phone": "+48 22 123 4567",
                "location": {
                    "address": "ul. Marszałkowska 123",
                    "city": "Warsaw",
                    "postal_code": "00-001",
                    "country": "Poland"
                }
            }
        }


class BusinessUpdate(BaseModel):
    business_name: Optional[str] = Field(None, min_length=2, max_length=200)
    description: Optional[str] = Field(None, min_length=20, max_length=1000)
    category: Optional[BusinessCategory] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, min_length=9, max_length=20)
    website: Optional[HttpUrl] = None
    location: Optional[LocationSchema] = None
    logo_url: Optional[HttpUrl] = None
    cover_image_url: Optional[HttpUrl] = None
    images: Optional[List[HttpUrl]] = None
    operating_hours: Optional[List[OperatingHours]] = None
    status: Optional[BusinessStatus] = None
    tags: Optional[List[str]] = None


class BusinessResponse(BaseModel):
    id: str
    owner_id: str
    business_name: str
    description: str
    category: BusinessCategory
    email: EmailStr
    phone: str
    website: Optional[HttpUrl]
    location: dict
    logo_url: Optional[HttpUrl]
    cover_image_url: Optional[HttpUrl]
    images: List[HttpUrl]
    operating_hours: List[OperatingHours]
    status: BusinessStatus
    is_verified: bool
    rating_average: float
    rating_count: int
    total_deals: int
    active_deals: int
    followers_count: int
    tags: List[str]
    created_at: datetime
    updated_at: datetime


class BusinessListResponse(BaseModel):
    businesses: List[BusinessResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class BusinessDeleteResponse(BaseModel):
    message: str
    business_id: str
