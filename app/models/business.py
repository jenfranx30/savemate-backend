"""
Business model for companies offering deals
"""
from datetime import datetime
from typing import Optional, List, Dict
from beanie import Document, Indexed
from pydantic import Field, EmailStr, HttpUrl, BaseModel
from pymongo import IndexModel, GEOSPHERE

from app.models.common import Location, Address


class ContactInfo(BaseModel):
    """Embedded contact information"""
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    website: Optional[HttpUrl] = None


class SocialMedia(BaseModel):
    """Embedded social media links"""
    facebook: Optional[str] = None
    instagram: Optional[str] = None
    twitter: Optional[str] = None
    linkedin: Optional[str] = None


class OperatingHours(BaseModel):
    """Operating hours for a single day"""
    open: str = Field(..., description="Opening time (e.g., '09:00')")
    close: str = Field(..., description="Closing time (e.g., '21:00')")
    closed: bool = Field(default=False, description="Whether closed this day")


class Business(Document):
    """
    Business document for companies offering deals
    """
    
    # Basic Information
    name: Indexed(str) = Field(
        ...,
        min_length=2,
        max_length=200,
        description="Business name"
    )
    description: str = Field(
        ...,
        max_length=2000,
        description="About the business"
    )
    category: str = Field(
        ...,
        description="Business category (e.g., Restaurant, Retail)"
    )
    
    # Ownership
    owner_id: str = Field(
        ...,
        description="Reference to User document (business owner)"
    )
    
    # Media
    logo: Optional[str] = Field(
        None,
        description="Business logo URL (Cloudinary)"
    )
    cover_image: Optional[str] = Field(
        None,
        description="Cover/banner image URL"
    )
    gallery: List[str] = Field(
        default_factory=list,
        description="Additional business images"
    )
    
    # Location
    location: Location = Field(
        ...,
        description="Business location (GeoJSON Point)"
    )
    address: Address = Field(
        ...,
        description="Physical address"
    )
    
    # Contact Information
    contact: ContactInfo = Field(
        default_factory=ContactInfo,
        description="Contact details"
    )
    social_media: SocialMedia = Field(
        default_factory=SocialMedia,
        description="Social media links"
    )
    
    # Operating Hours
    operating_hours: Dict[str, OperatingHours] = Field(
        default_factory=dict,
        description="Weekly operating hours (day: hours)"
    )
    
    # Statistics
    rating: float = Field(
        default=0.0,
        ge=0,
        le=5,
        description="Average rating (0-5 stars)"
    )
    total_reviews: int = Field(
        default=0,
        ge=0,
        description="Total number of reviews"
    )
    total_deals: int = Field(
        default=0,
        ge=0,
        description="Total active deals"
    )
    followers_count: int = Field(
        default=0,
        ge=0,
        description="Number of followers"
    )
    
    # Verification
    is_verified: bool = Field(
        default=False,
        description="Verified business badge"
    )
    verification_date: Optional[datetime] = Field(
        None,
        description="When business was verified"
    )
    
    # Status
    is_active: bool = Field(
        default=True,
        description="Business active status"
    )
    
    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow
    )
    
    def update_timestamp(self):
        """Update the updated_at timestamp"""
        self.updated_at = datetime.utcnow()
    
    def increment_deals_count(self):
        """Increment total deals counter"""
        self.total_deals += 1
        self.update_timestamp()
    
    def decrement_deals_count(self):
        """Decrement total deals counter"""
        if self.total_deals > 0:
            self.total_deals -= 1
        self.update_timestamp()
    
    class Settings:
        name = "businesses"
        indexes = [
            IndexModel([("location", GEOSPHERE)]),
            "owner_id",
            IndexModel([("name", "text"), ("description", "text")]),
            "is_verified",
            "category",
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Pizza Palace",
                "description": "Best pizza in Warsaw since 2010",
                "category": "Restaurant",
                "owner_id": "507f1f77bcf86cd799439011",
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
                },
                "contact": {
                    "phone": "+48 22 123 4567",
                    "email": "contact@pizzapalace.pl"
                }
            }
        }