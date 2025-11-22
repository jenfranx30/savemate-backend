"""
Category model for deal categorization
"""
from datetime import datetime
from typing import Optional
from beanie import Document, Indexed
from pydantic import Field, field_validator
import re


class Category(Document):
    """
    Category document for organizing deals
    Examples: Food & Dining, Shopping, Entertainment, etc.
    """
    
    # Basic Information
    name: Indexed(str, unique=True) = Field(
        ..., 
        min_length=2, 
        max_length=100,
        description="Category name (unique)"
    )
    slug: Indexed(str, unique=True) = Field(
        ...,
        description="URL-friendly identifier"
    )
    description: Optional[str] = Field(
        None, 
        max_length=500,
        description="Category description"
    )
    
    # Visual Representation
    icon: str = Field(
        default="tag",
        description="Icon name or emoji"
    )
    color: str = Field(
        default="#3B82F6",
        description="Hex color code for UI"
    )
    image: Optional[str] = Field(
        None,
        description="Category image URL (optional)"
    )
    
    # Hierarchy (for subcategories)
    parent_category: Optional[str] = Field(
        None,
        description="Parent category ID for nested categories"
    )
    order: int = Field(
        default=0,
        description="Display order"
    )
    
    # Statistics
    deals_count: int = Field(
        default=0,
        ge=0,
        description="Number of active deals in this category"
    )
    
    # Status
    is_active: bool = Field(
        default=True,
        description="Whether category is visible to users"
    )
    is_featured: bool = Field(
        default=False,
        description="Show in featured/highlighted sections"
    )
    
    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When category was created"
    )
    
    @field_validator('slug')
    @classmethod
    def validate_slug(cls, v):
        """Ensure slug is URL-friendly"""
        if not re.match(r'^[a-z0-9-]+$', v):
            raise ValueError(
                'Slug must contain only lowercase letters, numbers, and hyphens'
            )
        return v
    
    @field_validator('color')
    @classmethod
    def validate_color(cls, v):
        """Ensure color is valid hex code"""
        if not re.match(r'^#[0-9A-Fa-f]{6}$', v):
            raise ValueError('Color must be a valid hex code (e.g., #3B82F6)')
        return v
    
    class Settings:
        name = "categories"
        indexes = [
            "name",
            "slug",
            "parent_category",
            "is_active",
            "order",
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Food & Dining",
                "slug": "food-dining",
                "description": "Restaurants, cafes, and food delivery services",
                "icon": "🍔",
                "color": "#EF4444",
                "is_featured": True,
                "order": 1
            }
        }