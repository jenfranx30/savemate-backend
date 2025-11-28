"""
Category Schemas for SaveMate API
Pydantic models for request/response validation
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
import re


class CategoryBase(BaseModel):
    """Base category schema with common fields"""
    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Category name",
        examples=["Food & Dining", "Shopping", "Entertainment"]
    )
    slug: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="URL-friendly identifier",
        examples=["food-dining", "shopping", "entertainment"]
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Category description",
        examples=["Restaurants, cafes, and food delivery services"]
    )
    icon: str = Field(
        default="tag",
        description="Icon name or emoji",
        examples=["🍔", "🛍️", "🎬", "tag"]
    )
    color: str = Field(
        default="#3B82F6",
        description="Hex color code for UI",
        examples=["#EF4444", "#10B981", "#3B82F6"]
    )
    image: Optional[str] = Field(
        None,
        description="Category image URL",
        examples=["https://example.com/food-category.jpg"]
    )
    parent_category: Optional[str] = Field(
        None,
        description="Parent category ID for nested categories",
        examples=["674890abcdef123456789012"]
    )
    order: int = Field(
        default=0,
        ge=0,
        description="Display order (0 = first)",
        examples=[0, 1, 2]
    )
    is_active: bool = Field(
        default=True,
        description="Whether category is visible to users"
    )
    is_featured: bool = Field(
        default=False,
        description="Show in featured sections"
    )

    @field_validator('slug')
    @classmethod
    def validate_slug(cls, v: str) -> str:
        """Ensure slug is URL-friendly"""
        if not re.match(r'^[a-z0-9-]+$', v):
            raise ValueError(
                'Slug must contain only lowercase letters, numbers, and hyphens'
            )
        return v

    @field_validator('color')
    @classmethod
    def validate_color(cls, v: str) -> str:
        """Ensure color is valid hex code"""
        if not re.match(r'^#[0-9A-Fa-f]{6}$', v):
            raise ValueError('Color must be a valid hex code (e.g., #3B82F6)')
        return v


class CategoryCreate(CategoryBase):
    """Schema for creating a new category"""
    pass


class CategoryUpdate(BaseModel):
    """Schema for updating a category (all fields optional)"""
    name: Optional[str] = Field(
        None,
        min_length=2,
        max_length=100,
        description="Category name"
    )
    slug: Optional[str] = Field(
        None,
        min_length=2,
        max_length=100,
        description="URL-friendly identifier"
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Category description"
    )
    icon: Optional[str] = Field(
        None,
        description="Icon name or emoji"
    )
    color: Optional[str] = Field(
        None,
        description="Hex color code"
    )
    image: Optional[str] = Field(
        None,
        description="Category image URL"
    )
    parent_category: Optional[str] = Field(
        None,
        description="Parent category ID"
    )
    order: Optional[int] = Field(
        None,
        ge=0,
        description="Display order"
    )
    is_active: Optional[bool] = Field(
        None,
        description="Active status"
    )
    is_featured: Optional[bool] = Field(
        None,
        description="Featured status"
    )

    @field_validator('slug')
    @classmethod
    def validate_slug(cls, v: Optional[str]) -> Optional[str]:
        """Ensure slug is URL-friendly if provided"""
        if v and not re.match(r'^[a-z0-9-]+$', v):
            raise ValueError(
                'Slug must contain only lowercase letters, numbers, and hyphens'
            )
        return v

    @field_validator('color')
    @classmethod
    def validate_color(cls, v: Optional[str]) -> Optional[str]:
        """Ensure color is valid hex code if provided"""
        if v and not re.match(r'^#[0-9A-Fa-f]{6}$', v):
            raise ValueError('Color must be a valid hex code (e.g., #3B82F6)')
        return v


class CategoryResponse(CategoryBase):
    """Schema for category response with additional fields"""
    id: str = Field(
        ...,
        description="Category unique identifier"
    )
    deals_count: int = Field(
        default=0,
        ge=0,
        description="Number of active deals in this category"
    )
    created_at: datetime = Field(
        ...,
        description="When category was created"
    )

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "674890abcdef123456789012",
                "name": "Food & Dining",
                "slug": "food-dining",
                "description": "Restaurants, cafes, and food delivery services",
                "icon": "🍔",
                "color": "#EF4444",
                "image": "https://example.com/food.jpg",
                "parent_category": None,
                "order": 1,
                "deals_count": 15,
                "is_active": True,
                "is_featured": True,
                "created_at": "2024-11-28T10:00:00Z"
            }
        }


class CategorySummary(BaseModel):
    """Simplified category schema for listings"""
    id: str = Field(..., description="Category ID")
    name: str = Field(..., description="Category name")
    slug: str = Field(..., description="URL slug")
    icon: str = Field(..., description="Icon or emoji")
    color: str = Field(..., description="Hex color")
    deals_count: int = Field(..., description="Number of deals")
    is_featured: bool = Field(..., description="Featured status")

    class Config:
        from_attributes = True


class CategoryWithSubcategories(CategoryResponse):
    """Category response with nested subcategories"""
    subcategories: List[CategorySummary] = Field(
        default_factory=list,
        description="List of subcategories"
    )

    class Config:
        from_attributes = True


class CategoryListResponse(BaseModel):
    """Response schema for category list with pagination"""
    categories: List[CategoryResponse] = Field(
        ...,
        description="List of categories"
    )
    total: int = Field(
        ...,
        ge=0,
        description="Total number of categories"
    )
    page: int = Field(
        ...,
        ge=1,
        description="Current page number"
    )
    page_size: int = Field(
        ...,
        ge=1,
        le=100,
        description="Items per page"
    )
    total_pages: int = Field(
        ...,
        ge=0,
        description="Total number of pages"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "categories": [
                    {
                        "id": "674890abcdef123456789012",
                        "name": "Food & Dining",
                        "slug": "food-dining",
                        "description": "Restaurants and cafes",
                        "icon": "🍔",
                        "color": "#EF4444",
                        "deals_count": 15,
                        "is_active": True,
                        "is_featured": True,
                        "created_at": "2024-11-28T10:00:00Z"
                    }
                ],
                "total": 10,
                "page": 1,
                "page_size": 10,
                "total_pages": 1
            }
        }


class CategoryDeleteResponse(BaseModel):
    """Response schema for category deletion"""
    message: str = Field(..., description="Success message")
    category_id: str = Field(..., description="Deleted category ID")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Category deleted successfully",
                "category_id": "674890abcdef123456789012"
            }
        }


class CategoryStatsResponse(BaseModel):
    """Category statistics response"""
    total_categories: int = Field(..., description="Total categories")
    active_categories: int = Field(..., description="Active categories")
    featured_categories: int = Field(..., description="Featured categories")
    total_deals: int = Field(..., description="Total deals across all categories")
    top_categories: List[CategorySummary] = Field(
        ...,
        description="Categories with most deals"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "total_categories": 10,
                "active_categories": 8,
                "featured_categories": 3,
                "total_deals": 150,
                "top_categories": [
                    {
                        "id": "674890abcdef123456789012",
                        "name": "Food & Dining",
                        "slug": "food-dining",
                        "icon": "🍔",
                        "color": "#EF4444",
                        "deals_count": 45,
                        "is_featured": True
                    }
                ]
            }
        }
