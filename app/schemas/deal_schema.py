"""
Deal Schemas for SaveMate API
Pydantic models for deal-related requests and responses
"""

from pydantic import BaseModel, Field, HttpUrl, validator
from datetime import datetime
from typing import Optional, List
from app.models.deal import DealCategory, DealStatus


# ============================================================================
# LOCATION SCHEMAS
# ============================================================================

class LocationSchema(BaseModel):
    """Location information"""
    address: str = Field(..., min_length=5, description="Street address")
    city: str = Field(..., min_length=2, description="City name")
    postal_code: Optional[str] = Field(None, description="Postal code")
    country: str = Field(default="Poland", description="Country")
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="Latitude")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="Longitude")
    
    class Config:
        json_schema_extra = {
            "example": {
                "address": "ul. Marszałkowska 123",
                "city": "Warsaw",
                "postal_code": "00-001",
                "country": "Poland",
                "latitude": 52.2297,
                "longitude": 21.0122
            }
        }


# ============================================================================
# REQUEST SCHEMAS
# ============================================================================

class DealCreate(BaseModel):
    """Schema for creating a new deal"""
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=20, max_length=2000)
    original_price: float = Field(..., gt=0, description="Original price in PLN")
    discounted_price: float = Field(..., gt=0, description="Discounted price in PLN")
    category: DealCategory
    tags: List[str] = Field(default_factory=list, max_items=10)
    business_name: str = Field(..., min_length=2, max_length=200)
    location: LocationSchema
    end_date: datetime = Field(..., description="Deal expiration date")
    start_date: Optional[datetime] = Field(None, description="Deal start date")
    image_url: Optional[HttpUrl] = None
    additional_images: List[HttpUrl] = Field(default_factory=list, max_items=5)
    terms: Optional[str] = Field(None, max_length=1000)
    quantity_available: Optional[int] = Field(None, gt=0)
    
    @validator('discounted_price')
    def validate_discount(cls, v, values):
        """Ensure discounted price is less than original price"""
        if 'original_price' in values and v >= values['original_price']:
            raise ValueError('Discounted price must be less than original price')
        return v
    
    @validator('end_date')
    def validate_end_date(cls, v):
        """Ensure end date is in the future"""
        if v <= datetime.utcnow():
            raise ValueError('End date must be in the future')
        return v
    
    @validator('start_date')
    def validate_start_date(cls, v, values):
        """Ensure start date is before end date"""
        if v and 'end_date' in values and v >= values['end_date']:
            raise ValueError('Start date must be before end date')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "50% Off Large Pizza",
                "description": "Get half off any large pizza with 3+ toppings. Valid for dine-in and takeout.",
                "original_price": 39.99,
                "discounted_price": 19.99,
                "category": "food",
                "tags": ["pizza", "italian", "dinner"],
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


class DealUpdate(BaseModel):
    """Schema for updating an existing deal"""
    title: Optional[str] = Field(None, min_length=5, max_length=200)
    description: Optional[str] = Field(None, min_length=20, max_length=2000)
    original_price: Optional[float] = Field(None, gt=0)
    discounted_price: Optional[float] = Field(None, gt=0)
    category: Optional[DealCategory] = None
    tags: Optional[List[str]] = None
    location: Optional[LocationSchema] = None
    end_date: Optional[datetime] = None
    start_date: Optional[datetime] = None
    status: Optional[DealStatus] = None
    is_featured: Optional[bool] = None
    image_url: Optional[HttpUrl] = None
    additional_images: Optional[List[HttpUrl]] = None
    terms: Optional[str] = Field(None, max_length=1000)
    quantity_available: Optional[int] = Field(None, gt=0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "60% Off Large Pizza - Extended!",
                "discounted_price": 15.99,
                "end_date": "2025-12-31T23:59:59"
            }
        }


# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================

class DealResponse(BaseModel):
    """Schema for deal response"""
    id: str = Field(..., description="Deal ID")
    title: str
    description: str
    original_price: float
    discounted_price: float
    discount_percentage: Optional[int]
    category: DealCategory
    tags: List[str]
    business_id: str
    business_name: str
    location: dict
    start_date: datetime
    end_date: datetime
    status: DealStatus
    is_featured: bool
    image_url: Optional[HttpUrl]
    additional_images: List[HttpUrl]
    views_count: int
    saves_count: int
    terms: Optional[str]
    quantity_available: Optional[int]
    created_at: datetime
    updated_at: datetime
    created_by: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "title": "50% Off Large Pizza",
                "description": "Get half off any large pizza with 3+ toppings.",
                "original_price": 39.99,
                "discounted_price": 19.99,
                "discount_percentage": 50,
                "category": "food",
                "tags": ["pizza", "italian", "dinner"],
                "business_id": "507f1f77bcf86cd799439012",
                "business_name": "Mario's Pizzeria",
                "location": {
                    "address": "ul. Marszałkowska 123",
                    "city": "Warsaw",
                    "postal_code": "00-001",
                    "country": "Poland"
                },
                "start_date": "2025-11-23T00:00:00",
                "end_date": "2025-12-31T23:59:59",
                "status": "active",
                "is_featured": False,
                "image_url": "https://example.com/pizza.jpg",
                "views_count": 150,
                "saves_count": 25,
                "created_at": "2025-11-23T20:00:00"
            }
        }


class DealListResponse(BaseModel):
    """Schema for paginated deal list"""
    deals: List[DealResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "deals": [],
                "total": 45,
                "page": 1,
                "page_size": 10,
                "total_pages": 5
            }
        }


class DealSummary(BaseModel):
    """Minimal deal information for lists"""
    id: str
    title: str
    discounted_price: float
    discount_percentage: Optional[int]
    category: DealCategory
    business_name: str
    city: str
    image_url: Optional[HttpUrl]
    end_date: datetime
    status: DealStatus
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "title": "50% Off Large Pizza",
                "discounted_price": 19.99,
                "discount_percentage": 50,
                "category": "food",
                "business_name": "Mario's Pizzeria",
                "city": "Warsaw",
                "image_url": "https://example.com/pizza.jpg",
                "end_date": "2025-12-31T23:59:59",
                "status": "active"
            }
        }


# ============================================================================
# FILTER SCHEMAS
# ============================================================================

class DealFilters(BaseModel):
    """Query parameters for filtering deals"""
    category: Optional[DealCategory] = None
    city: Optional[str] = None
    min_discount: Optional[int] = Field(None, ge=0, le=100)
    max_price: Optional[float] = Field(None, gt=0)
    search: Optional[str] = Field(None, min_length=2)
    is_featured: Optional[bool] = None
    status: Optional[DealStatus] = Field(default=DealStatus.ACTIVE)
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)
    sort_by: Optional[str] = Field(default="created_at", pattern="^(created_at|discount_percentage|price|end_date)$")
    sort_order: Optional[str] = Field(default="desc", pattern="^(asc|desc)$")


# ============================================================================
# MESSAGE SCHEMAS
# ============================================================================

class DealDeleteResponse(BaseModel):
    """Response for deal deletion"""
    message: str
    deal_id: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Deal deleted successfully",
                "deal_id": "507f1f77bcf86cd799439011"
            }
        }
