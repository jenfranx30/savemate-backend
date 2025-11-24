"""
Deal model for local deals and promotions
"""
from datetime import datetime
from typing import Optional, List
from beanie import Document, Indexed
from pydantic import Field, field_validator, computed_field
from pymongo import IndexModel, GEOSPHERE, DESCENDING

from app.models.common import Location, Address


class Deal(Document):
    """
    Deal document for local promotions and discounts
    """
    
    # Basic Information
    title: Indexed(str) = Field(
        ...,
        min_length=3,
        max_length=200,
        description="Deal title"
    )
    description: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="Detailed description"
    )
    
    # Relationships (references to other documents)
    business_id: str = Field(
        ...,
        description="Reference to Business document"
    )
    category_id: str = Field(
        ...,
        description="Reference to Category document"
    )
    created_by: str = Field(
        ...,
        description="Reference to User document (deal creator)"
    )
    
    # Pricing
    original_price: float = Field(
        ...,
        gt=0,
        description="Original price before discount"
    )
    discounted_price: float = Field(
        ...,
        gt=0,
        description="Price after discount"
    )
    discount_percentage: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="Discount percentage (auto-calculated)"
    )
    currency: str = Field(
        default="PLN",
        description="Currency code"
    )
    
    # Media
    images: List[str] = Field(
        default_factory=list,
        description="List of image URLs (Cloudinary)"
    )
    
    # Location
    location: Location = Field(
        ...,
        description="Deal location (GeoJSON Point)"
    )
    address: Address = Field(
        ...,
        description="Physical address where deal is valid"
    )
    
    # Validity Period
    valid_from: datetime = Field(
        default_factory=datetime.utcnow,
        description="When deal becomes active"
    )
    valid_until: datetime = Field(
        ...,
        description="When deal expires"
    )
    
    # Terms & Conditions
    terms_conditions: Optional[str] = Field(
        None,
        max_length=1000,
        description="Terms and conditions"
    )
    redemption_code: Optional[str] = Field(
        None,
        description="Promo code for redemption"
    )
    max_redemptions: Optional[int] = Field(
        None,
        ge=1,
        description="Maximum number of times deal can be redeemed"
    )
    current_redemptions: int = Field(
        default=0,
        ge=0,
        description="Number of times already redeemed"
    )
    
    # Engagement Metrics
    views_count: int = Field(
        default=0,
        ge=0,
        description="Number of views"
    )
    saves_count: int = Field(
        default=0,
        ge=0,
        description="Number of times saved"
    )
    shares_count: int = Field(
        default=0,
        ge=0,
        description="Number of shares"
    )
    
    # Status
    is_active: bool = Field(
        default=True,
        description="Whether deal is currently active"
    )
    is_featured: bool = Field(
        default=False,
        description="Featured deal (highlighted in UI)"
    )
    
    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow
    )
    
    # Computed Properties
    @computed_field
    @property
    def is_expired(self) -> bool:
        """Check if deal has expired"""
        return datetime.utcnow() > self.valid_until
    
    @computed_field
    @property
    def days_remaining(self) -> int:
        """Calculate days remaining until expiration"""
        if self.is_expired:
            return 0
        delta = self.valid_until - datetime.utcnow()
        return max(0, delta.days)
    
    # Validators
    @field_validator('discounted_price')
    @classmethod
    def validate_discount(cls, v, info):
        """Ensure discounted price is less than original price"""
        if 'original_price' in info.data:
            if v >= info.data['original_price']:
                raise ValueError(
                    'Discounted price must be less than original price'
                )
        return v
    
    @field_validator('valid_until')
    @classmethod
    def validate_expiry(cls, v):
        """Ensure valid_until is in the future"""
        if v <= datetime.utcnow():
            raise ValueError('Expiry date must be in the future')
        return v
    
    # Methods
    def calculate_discount_percentage(self):
        """Calculate and set discount percentage"""
        if self.original_price > 0:
            self.discount_percentage = round(
                ((self.original_price - self.discounted_price) / self.original_price) * 100,
                2
            )
    
    def increment_views(self):
        """Increment view counter"""
        self.views_count += 1
    
    def increment_saves(self):
        """Increment save counter"""
        self.saves_count += 1
    
    def decrement_saves(self):
        """Decrement save counter"""
        if self.saves_count > 0:
            self.saves_count -= 1
    
    def update_timestamp(self):
        """Update the updated_at timestamp"""
        self.updated_at = datetime.utcnow()
    
    class Settings:
        name = "deals"
        indexes = [
            IndexModel([("location", GEOSPHERE)]),  # Geospatial queries
            "business_id",
            "category_id",
            "created_by",
            "valid_until",
            IndexModel([("created_at", DESCENDING)]),  # Newest first
            IndexModel([("is_active", 1), ("valid_until", 1)]),  # Active deals
            IndexModel([("title", "text"), ("description", "text")]),  # Search
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "50% Off All Pizzas",
                "description": "Get half price on any pizza during lunch hours",
                "business_id": "507f1f77bcf86cd799439011",
                "category_id": "507f1f77bcf86cd799439012",
                "created_by": "507f1f77bcf86cd799439013",
                "original_price": 40.0,
                "discounted_price": 20.0,
                "valid_until": "2025-12-31T23:59:59",
                "location": {
                    "type": "Point",
                    "coordinates": [21.0122, 52.2297]
                },
                "address": {
                    "street": "ul. Marszałkowska 123",
                    "city": "Warsaw",
                    "state": "Mazovia",
                    "zip_code": "00-001",
                    "country": "Poland"
                }
            }
        }