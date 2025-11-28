"""
Category API Routes for SaveMate
CRUD operations for deal categories
"""

from fastapi import APIRouter, HTTPException, Depends, Query, status
from typing import List, Optional
from beanie import PydanticObjectId
from datetime import datetime
import math

from app.models.category import Category
from app.schemas.category_schema import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    CategoryListResponse,
    CategoryDeleteResponse,
    CategorySummary,
    CategoryWithSubcategories,
    CategoryStatsResponse
)
from app.core.security import get_current_user, require_admin
from app.models.user import User

router = APIRouter(prefix="/categories", tags=["Categories"])


# ============================================================================
# PUBLIC ENDPOINTS (No authentication required)
# ============================================================================

@router.get(
    "/",
    response_model=CategoryListResponse,
    status_code=status.HTTP_200_OK,
    summary="List all categories",
    description="Get all categories with optional filtering and pagination"
)
async def list_categories(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    active_only: bool = Query(True, description="Show only active categories"),
    featured_only: bool = Query(False, description="Show only featured categories"),
    parent_id: Optional[str] = Query(None, description="Filter by parent category ID"),
    search: Optional[str] = Query(None, description="Search by name or description")
):
    """
    List all categories with pagination and filtering.
    
    **Filters:**
    - `active_only`: Show only active categories (default: true)
    - `featured_only`: Show only featured categories
    - `parent_id`: Filter by parent category (for subcategories)
    - `search`: Text search in name and description
    
    **Public endpoint** - No authentication required
    """
    try:
        # Build query
        query = {}
        
        # Filter by active status
        if active_only:
            query["is_active"] = True
        
        # Filter by featured status
        if featured_only:
            query["is_featured"] = True
        
        # Filter by parent category
        if parent_id:
            query["parent_category"] = parent_id
        
        # Text search
        if search:
            query["$or"] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}}
            ]
        
        # Get total count
        total = await Category.find(query).count()
        
        # Calculate pagination
        skip = (page - 1) * page_size
        total_pages = math.ceil(total / page_size) if total > 0 else 0
        
        # Get categories with pagination, sorted by order
        categories = await Category.find(query)\
            .sort("+order", "+name")\
            .skip(skip)\
            .limit(page_size)\
            .to_list()
        
        # Convert to response format
        category_responses = [
            CategoryResponse(
                id=str(cat.id),
                name=cat.name,
                slug=cat.slug,
                description=cat.description,
                icon=cat.icon,
                color=cat.color,
                image=cat.image,
                parent_category=cat.parent_category,
                order=cat.order,
                deals_count=cat.deals_count,
                is_active=cat.is_active,
                is_featured=cat.is_featured,
                created_at=cat.created_at
            )
            for cat in categories
        ]
        
        return CategoryListResponse(
            categories=category_responses,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch categories: {str(e)}"
        )


@router.get(
    "/featured",
    response_model=List[CategoryResponse],
    status_code=status.HTTP_200_OK,
    summary="Get featured categories",
    description="Get all featured categories for homepage display"
)
async def get_featured_categories():
    """
    Get all featured categories (typically 3-6 categories for homepage).
    
    **Public endpoint** - No authentication required
    """
    try:
        categories = await Category.find(
            Category.is_active == True,
            Category.is_featured == True
        ).sort("+order").to_list()
        
        return [
            CategoryResponse(
                id=str(cat.id),
                name=cat.name,
                slug=cat.slug,
                description=cat.description,
                icon=cat.icon,
                color=cat.color,
                image=cat.image,
                parent_category=cat.parent_category,
                order=cat.order,
                deals_count=cat.deals_count,
                is_active=cat.is_active,
                is_featured=cat.is_featured,
                created_at=cat.created_at
            )
            for cat in categories
        ]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch featured categories: {str(e)}"
        )


@router.get(
    "/slug/{slug}",
    response_model=CategoryWithSubcategories,
    status_code=status.HTTP_200_OK,
    summary="Get category by slug",
    description="Get a single category by its URL slug with subcategories"
)
async def get_category_by_slug(slug: str):
    """
    Get a category by its slug (URL-friendly identifier).
    Includes subcategories if any exist.
    
    **Public endpoint** - No authentication required
    """
    try:
        # Find category by slug
        category = await Category.find_one(Category.slug == slug)
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with slug '{slug}' not found"
            )
        
        # Get subcategories
        subcategories = await Category.find(
            Category.parent_category == str(category.id),
            Category.is_active == True
        ).sort("+order").to_list()
        
        subcategory_summaries = [
            CategorySummary(
                id=str(sub.id),
                name=sub.name,
                slug=sub.slug,
                icon=sub.icon,
                color=sub.color,
                deals_count=sub.deals_count,
                is_featured=sub.is_featured
            )
            for sub in subcategories
        ]
        
        return CategoryWithSubcategories(
            id=str(category.id),
            name=category.name,
            slug=category.slug,
            description=category.description,
            icon=category.icon,
            color=category.color,
            image=category.image,
            parent_category=category.parent_category,
            order=category.order,
            deals_count=category.deals_count,
            is_active=category.is_active,
            is_featured=category.is_featured,
            created_at=category.created_at,
            subcategories=subcategory_summaries
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch category: {str(e)}"
        )


@router.get(
    "/{category_id}",
    response_model=CategoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get category by ID",
    description="Get a single category by its ID"
)
async def get_category(category_id: str):
    """
    Get a category by its ID.
    
    **Public endpoint** - No authentication required
    """
    try:
        # Validate ObjectId format
        try:
            obj_id = PydanticObjectId(category_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid category ID format"
            )
        
        # Find category
        category = await Category.get(obj_id)
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with ID '{category_id}' not found"
            )
        
        return CategoryResponse(
            id=str(category.id),
            name=category.name,
            slug=category.slug,
            description=category.description,
            icon=category.icon,
            color=category.color,
            image=category.image,
            parent_category=category.parent_category,
            order=category.order,
            deals_count=category.deals_count,
            is_active=category.is_active,
            is_featured=category.is_featured,
            created_at=category.created_at
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch category: {str(e)}"
        )


@router.get(
    "/stats/overview",
    response_model=CategoryStatsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get category statistics",
    description="Get overall category statistics and top categories"
)
async def get_category_stats():
    """
    Get category statistics including:
    - Total categories
    - Active categories
    - Featured categories
    - Total deals
    - Top categories by deal count
    
    **Public endpoint** - No authentication required
    """
    try:
        # Get counts
        total_categories = await Category.find().count()
        active_categories = await Category.find(Category.is_active == True).count()
        featured_categories = await Category.find(
            Category.is_active == True,
            Category.is_featured == True
        ).count()
        
        # Get total deals count across all categories
        all_categories = await Category.find().to_list()
        total_deals = sum(cat.deals_count for cat in all_categories)
        
        # Get top 5 categories by deals_count
        top_categories = await Category.find(
            Category.is_active == True
        ).sort("-deals_count").limit(5).to_list()
        
        top_category_summaries = [
            CategorySummary(
                id=str(cat.id),
                name=cat.name,
                slug=cat.slug,
                icon=cat.icon,
                color=cat.color,
                deals_count=cat.deals_count,
                is_featured=cat.is_featured
            )
            for cat in top_categories
        ]
        
        return CategoryStatsResponse(
            total_categories=total_categories,
            active_categories=active_categories,
            featured_categories=featured_categories,
            total_deals=total_deals,
            top_categories=top_category_summaries
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch statistics: {str(e)}"
        )


# ============================================================================
# PROTECTED ENDPOINTS (Authentication required - Admin only)
# ============================================================================

@router.post(
    "/",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create category",
    description="Create a new category (admin only)"
)
async def create_category(
    category_data: CategoryCreate,
    current_user: User = Depends(require_admin)
):
    """
    Create a new category.
    
    **Requires:** Admin authentication
    **Returns:** Created category with ID
    """
    try:
        # Check if slug already exists
        existing_slug = await Category.find_one(Category.slug == category_data.slug)
        if existing_slug:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category with slug '{category_data.slug}' already exists"
            )
        
        # Check if name already exists
        existing_name = await Category.find_one(Category.name == category_data.name)
        if existing_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category with name '{category_data.name}' already exists"
            )
        
        # Create category
        new_category = Category(
            name=category_data.name,
            slug=category_data.slug,
            description=category_data.description,
            icon=category_data.icon,
            color=category_data.color,
            image=category_data.image,
            parent_category=category_data.parent_category,
            order=category_data.order,
            is_active=category_data.is_active,
            is_featured=category_data.is_featured,
            created_at=datetime.utcnow()
        )
        
        await new_category.insert()
        
        return CategoryResponse(
            id=str(new_category.id),
            name=new_category.name,
            slug=new_category.slug,
            description=new_category.description,
            icon=new_category.icon,
            color=new_category.color,
            image=new_category.image,
            parent_category=new_category.parent_category,
            order=new_category.order,
            deals_count=new_category.deals_count,
            is_active=new_category.is_active,
            is_featured=new_category.is_featured,
            created_at=new_category.created_at
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create category: {str(e)}"
        )


@router.put(
    "/{category_id}",
    response_model=CategoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Update category",
    description="Update an existing category (admin only)"
)
async def update_category(
    category_id: str,
    category_data: CategoryUpdate,
    current_user: User = Depends(require_admin)
):
    """
    Update an existing category.
    
    **Requires:** Admin authentication
    **Returns:** Updated category
    """
    try:
        # Validate ObjectId format
        try:
            obj_id = PydanticObjectId(category_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid category ID format"
            )
        
        # Find category
        category = await Category.get(obj_id)
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with ID '{category_id}' not found"
            )
        
        # Check if new slug conflicts with existing
        if category_data.slug and category_data.slug != category.slug:
            existing_slug = await Category.find_one(Category.slug == category_data.slug)
            if existing_slug:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Category with slug '{category_data.slug}' already exists"
                )
        
        # Check if new name conflicts with existing
        if category_data.name and category_data.name != category.name:
            existing_name = await Category.find_one(Category.name == category_data.name)
            if existing_name:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Category with name '{category_data.name}' already exists"
                )
        
        # Update fields
        update_data = category_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(category, field, value)
        
        await category.save()
        
        return CategoryResponse(
            id=str(category.id),
            name=category.name,
            slug=category.slug,
            description=category.description,
            icon=category.icon,
            color=category.color,
            image=category.image,
            parent_category=category.parent_category,
            order=category.order,
            deals_count=category.deals_count,
            is_active=category.is_active,
            is_featured=category.is_featured,
            created_at=category.created_at
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update category: {str(e)}"
        )


@router.delete(
    "/{category_id}",
    response_model=CategoryDeleteResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete category",
    description="Delete a category (admin only)"
)
async def delete_category(
    category_id: str,
    current_user: User = Depends(require_admin)
):
    """
    Delete a category.
    
    **Warning:** This will not delete deals in this category.
    Consider deactivating the category instead.
    
    **Requires:** Admin authentication
    **Returns:** Confirmation message
    """
    try:
        # Validate ObjectId format
        try:
            obj_id = PydanticObjectId(category_id)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid category ID format"
            )
        
        # Find category
        category = await Category.get(obj_id)
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with ID '{category_id}' not found"
            )
        
        # Check if category has deals
        if category.deals_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete category with {category.deals_count} active deals. "
                       "Deactivate the category instead or reassign deals."
            )
        
        # Delete category
        await category.delete()
        
        return CategoryDeleteResponse(
            message="Category deleted successfully",
            category_id=category_id
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete category: {str(e)}"
        )
