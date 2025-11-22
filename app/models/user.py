"""
User model for authentication and profiles
"""
from datetime import datetime
from typing import Optional, List
from beanie import Document, Indexed
from pydantic import EmailStr, Field, field_validator, BaseModel
from pymongo import IndexModel, GEOSPHERE
import re

from app.models.common import Location


class UserPreferences(BaseModel):
    """Embedded user preferences"""
    favorite_categories: List[str] = Field(
        default_factory=list,
        description="List of favorite category slugs"
    )
    notification_radius: float = Field(
        default=5.0,
        ge=0.1,
        le=100.0,
        description="Radius in km for deal notifications"
    )
    email_notifications: bool = Field(
        default=True,
        description="Receive email notifications"
    )
    push_notifications: bool = Field(
        default=True,
        description="Receive push notifications"
    )


class User(Document):
    """
    User document for authentication and user profiles
    """
    
    # Authentication
    email: Indexed(EmailStr, unique=True) = Field(
        ...,
        description="User's email address (unique)"
    )
    username: Indexed(str, unique=True) = Field(
        ...,
        min_length=3,
        max_length=30,
        description="Username (unique, 3-30 chars)"
    )
    password_hash: str = Field(
        ...,
        description="Bcrypt hashed password"
    )
    
    # Profile Information
    full_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="User's full name"
    )
    profile_picture: Optional[str] = Field(
        None,
        description="Cloudinary URL for profile picture"
    )
    bio: Optional[str] = Field(
        None,
        max_length=500,
        description="User bio/description"
    )
    phone: Optional[str] = Field(
        None,
        description="Phone number"
    )
    
    # Location (GeoJSON format for geospatial queries)
    location: Optional[Location] = Field(
        None,
        description="User's location for nearby deals"
    )
    
    # Preferences
    preferences: UserPreferences = Field(
        default_factory=UserPreferences,
        description="User notification and category preferences"
    )
    
    # Saved Deals (references to Deal documents)
    saved_deals: List[str] = Field(
        default_factory=list,
        description="List of saved deal IDs"
    )
    
    # Business Owner Status
    is_business_owner: bool = Field(
        default=False,
        description="Whether user owns any businesses"
    )
    owned_businesses: List[str] = Field(
        default_factory=list,
        description="List of owned business IDs"
    )
    
    # Account Status
    is_active: bool = Field(
        default=True,
        description="Account active status"
    )
    is_verified: bool = Field(
        default=False,
        description="Account verification status"
    )
    email_verified: bool = Field(
        default=False,
        description="Email verification status"
    )
    
    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Account creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last profile update"
    )
    last_login: Optional[datetime] = Field(
        None,
        description="Last login timestamp"
    )
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        """Validate username format"""
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError(
                'Username can only contain letters, numbers, and underscores'
            )
        return v
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        """Basic phone validation"""
        if v and not re.match(r'^\+?[\d\s\-()]+$', v):
            raise ValueError('Invalid phone number format')
        return v
    
    def update_timestamp(self):
        """Update the updated_at timestamp"""
        self.updated_at = datetime.utcnow()
    
    def add_saved_deal(self, deal_id: str):
        """Add a deal to saved deals"""
        if deal_id not in self.saved_deals:
            self.saved_deals.append(deal_id)
            self.update_timestamp()
    
    def remove_saved_deal(self, deal_id: str):
        """Remove a deal from saved deals"""
        if deal_id in self.saved_deals:
            self.saved_deals.remove(deal_id)
            self.update_timestamp()
    
    class Settings:
        name = "users"
        indexes = [
            IndexModel([("location", GEOSPHERE)]),  # Geospatial index
            "email",
            "username",
            "created_at",
            "is_business_owner",
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "john.doe@example.com",
                "username": "johndoe",
                "full_name": "John Doe",
                "location": {
                    "type": "Point",
                    "coordinates": [21.0122, 52.2297]
                },
                "preferences": {
                    "favorite_categories": ["food-dining", "entertainment"],
                    "notification_radius": 5.0,
                    "email_notifications": True
                }
            }
        }