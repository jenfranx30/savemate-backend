"""
Deal Routes for SaveMate API
Endpoints for creating, reading, updating, and deleting deals
"""

from fastapi import APIRouter, HTTPException, status, Query, Depends
from beanie import PydanticObjectId
from typing import Optional, List
from datetime import datetime

from app.models.deal import Deal, DealCategory, DealStatus
from app.schemas.deal_schema import (
    DealCreate,
    DealUpdate,
    DealResponse,
    DealListResponse,
    DealSummary,
    DealFilters,
    DealDeleteResponse
)
from app.core.security import get_current_user

router = APIRouter()


# ============================================================================
# CREATE DEAL
# ============================================================================

@router.post("/", response_model=DealResponse, status_code=status.HTTP_201_CREATED)
async def create_deal(
    deal_data: DealCreate,
    current_user_id: str = Depends(get_current_user)
):
    """
    Create a new deal

    Business owners can create deals for their businesses.
    Requires authentication.
    """
    try:
        # Calculate discount percentage
        discount_pct = round(
            ((deal_data.original_price - deal_data.discounted_price) / deal_data.original_price) * 100
        )

        # Create deal instance
        new_deal = Deal(
            title=deal_data.title,
            description=deal_data.description,
            original_price=deal_data.original_price,
            discounted_price=deal_data.discounted_price,
            discount_percentage=discount_pct,
            category=deal_data.category,
            tags=deal_data.tags,
            business_id=current_user_id,  # Use authenticated user ID
            business_name=deal_data.business_name,
            location=deal_data.location.dict(),
            start_date=deal_data.start_date or datetime.utcnow(),
            end_date=deal_data.end_date,
            image_url=deal_data.image_url,
            additional_images=deal_data.additional_images,
            terms=deal_data.terms,
            quantity_available=deal_data.quantity_available,
            created_by=current_user_id  # Use authenticated user ID
        )

        # Save to database
        await new_deal.insert()

        # Return response
        return DealResponse(
            id=str(new_deal.id),
            title=new_deal.title,
            description=new_deal.description,
            original_price=new_deal.original_price,
            discounted_price=new_deal.discounted_price,
            discount_percentage=new_deal.discount_percentage,
            category=new_deal.category,
            tags=new_deal.tags,
            business_id=new_deal.business_id,
            business_name=new_deal.business_name,
            location=new_deal.location,
            start_date=new_deal.start_date,
            end_date=new_deal.end_date,
            status=new_deal.status,
            is_featured=new_deal.is_featured,
            image_url=new_deal.image_url,
            additional_images=new_deal.additional_images,
            views_count=new_deal.views_count,
            saves_count=new_deal.saves_count,
            terms=new_deal.terms,
            quantity_available=new_deal.quantity_available,
            created_at=new_deal.created_at,
            updated_at=new_deal.updated_at,
            created_by=new_deal.created_by
        )

    except Exception as e:
        print(f"Create deal error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create deal: {str(e)}"
        )


# ============================================================================
# GET ALL DEALS (WITH FILTERS)
# ============================================================================

@router.get("/", response_model=DealListResponse)
async def get_deals(
    category: Optional[DealCategory] = None,
    city: Optional[str] = None,
    min_discount: Optional[int] = Query(None, ge=0, le=100),
    max_price: Optional[float] = Query(None, gt=0),
    search: Optional[str] = Query(None, min_length=2),
    is_featured: Optional[bool] = None,
    deal_status: DealStatus = DealStatus.ACTIVE,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    sort_by: str = Query("created_at", pattern="^(created_at|discount_percentage|discounted_price|end_date)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$")
):
    """
    Get all deals with optional filtering

    Filter by category, location, price, discount, and more.
    Includes pagination and sorting.
    Public endpoint - no authentication required.
    """
    try:
        # Build query
        query = {}

        # Status filter
        query["status"] = deal_status

        # Category filter
        if category:
            query["category"] = category

        # City filter
        if city:
            query["location.city"] = {"$regex": city, "$options": "i"}

        # Discount filter
        if min_discount:
            query["discount_percentage"] = {"$gte": min_discount}

        # Price filter
        if max_price:
            query["discounted_price"] = {"$lte": max_price}

        # Featured filter
        if is_featured is not None:
            query["is_featured"] = is_featured

        # Text search
        if search:
            query["$or"] = [
                {"title": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}},
                {"business_name": {"$regex": search, "$options": "i"}},
                {"tags": {"$in": [search.lower()]}}
            ]

        # Get total count
        total = await Deal.find(query).count()

        # Calculate pagination
        skip = (page - 1) * page_size
        total_pages = (total + page_size - 1) // page_size

        # Sort
        sort_direction = 1 if sort_order == "asc" else -1

        # Get deals
        deals = await Deal.find(query).sort(
            (sort_by, sort_direction)
        ).skip(skip).limit(page_size).to_list()

        # Convert to response format
        deal_responses = [
            DealResponse(
                id=str(deal.id),
                title=deal.title,
                description=deal.description,
                original_price=deal.original_price,
                discounted_price=deal.discounted_price,
                discount_percentage=deal.discount_percentage,
                category=deal.category,
                tags=deal.tags,
                business_id=deal.business_id,
                business_name=deal.business_name,
                location=deal.location,
                start_date=deal.start_date,
                end_date=deal.end_date,
                status=deal.status,
                is_featured=deal.is_featured,
                image_url=deal.image_url,
                additional_images=deal.additional_images,
                views_count=deal.views_count,
                saves_count=deal.saves_count,
                terms=deal.terms,
                quantity_available=deal.quantity_available,
                created_at=deal.created_at,
                updated_at=deal.updated_at,
                created_by=deal.created_by
            )
            for deal in deals
        ]

        return DealListResponse(
            deals=deal_responses,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )

    except Exception as e:
        print(f"Get deals error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch deals: {str(e)}"
        )


# ============================================================================
# GET DEAL BY ID
# ============================================================================

@router.get("/{deal_id}", response_model=DealResponse)
async def get_deal(deal_id: str):
    """
    Get a specific deal by ID

    Increments view count automatically.
    Public endpoint - no authentication required.
    """
    try:
        # Get deal
        deal = await Deal.get(PydanticObjectId(deal_id))

        if not deal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deal not found"
            )

        # Increment views
        await deal.increment_views()

        return DealResponse(
            id=str(deal.id),
            title=deal.title,
            description=deal.description,
            original_price=deal.original_price,
            discounted_price=deal.discounted_price,
            discount_percentage=deal.discount_percentage,
            category=deal.category,
            tags=deal.tags,
            business_id=deal.business_id,
            business_name=deal.business_name,
            location=deal.location,
            start_date=deal.start_date,
            end_date=deal.end_date,
            status=deal.status,
            is_featured=deal.is_featured,
            image_url=deal.image_url,
            additional_images=deal.additional_images,
            views_count=deal.views_count,
            saves_count=deal.saves_count,
            terms=deal.terms,
            quantity_available=deal.quantity_available,
            created_at=deal.created_at,
            updated_at=deal.updated_at,
            created_by=deal.created_by
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Get deal error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch deal: {str(e)}"
        )


# ============================================================================
# UPDATE DEAL
# ============================================================================

@router.put("/{deal_id}", response_model=DealResponse)
async def update_deal(
    deal_id: str,
    deal_update: DealUpdate,
    current_user_id: str = Depends(get_current_user)
):
    """
    Update an existing deal

    Only the deal owner can update their deals.
    Requires authentication.
    """
    try:
        # Get deal
        deal = await Deal.get(PydanticObjectId(deal_id))

        if not deal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deal not found"
            )

        # Check ownership
        if deal.created_by != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update this deal"
            )

        # Update fields
        update_data = deal_update.dict(exclude_unset=True)

        # Recalculate discount if prices changed
        if "original_price" in update_data or "discounted_price" in update_data:
            original = update_data.get("original_price", deal.original_price)
            discounted = update_data.get("discounted_price", deal.discounted_price)
            update_data["discount_percentage"] = round(
                ((original - discounted) / original) * 100
            )

        # Update timestamp
        update_data["updated_at"] = datetime.utcnow()

        # Apply updates
        for field, value in update_data.items():
            setattr(deal, field, value)

        # Save
        await deal.save()

        return DealResponse(
            id=str(deal.id),
            title=deal.title,
            description=deal.description,
            original_price=deal.original_price,
            discounted_price=deal.discounted_price,
            discount_percentage=deal.discount_percentage,
            category=deal.category,
            tags=deal.tags,
            business_id=deal.business_id,
            business_name=deal.business_name,
            location=deal.location,
            start_date=deal.start_date,
            end_date=deal.end_date,
            status=deal.status,
            is_featured=deal.is_featured,
            image_url=deal.image_url,
            additional_images=deal.additional_images,
            views_count=deal.views_count,
            saves_count=deal.saves_count,
            terms=deal.terms,
            quantity_available=deal.quantity_available,
            created_at=deal.created_at,
            updated_at=deal.updated_at,
            created_by=deal.created_by
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Update deal error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update deal: {str(e)}"
        )


# ============================================================================
# DELETE DEAL
# ============================================================================

@router.delete("/{deal_id}", response_model=DealDeleteResponse)
async def delete_deal(
    deal_id: str,
    current_user_id: str = Depends(get_current_user)
):
    """
    Delete a deal

    Only the deal owner can delete their deals.
    Requires authentication.
    """
    try:
        # Get deal
        deal = await Deal.get(PydanticObjectId(deal_id))

        if not deal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deal not found"
            )

        # Check ownership
        if deal.created_by != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to delete this deal"
            )

        # Delete
        await deal.delete()

        return DealDeleteResponse(
            message="Deal deleted successfully",
            deal_id=deal_id
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Delete deal error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete deal: {str(e)}"
        )


# ============================================================================
# GET DEALS BY CATEGORY
# ============================================================================

@router.get("/category/{category}", response_model=List[DealSummary])
async def get_deals_by_category(
    category: DealCategory,
    limit: int = Query(20, ge=1, le=100)
):
    """
    Get deals by category

    Returns a simplified list of deals for a specific category.
    Public endpoint - no authentication required.
    """
    try:
        deals = await Deal.find(
            Deal.category == category,
            Deal.status == DealStatus.ACTIVE
        ).limit(limit).to_list()

        return [
            DealSummary(
                id=str(deal.id),
                title=deal.title,
                discounted_price=deal.discounted_price,
                discount_percentage=deal.discount_percentage,
                category=deal.category,
                business_name=deal.business_name,
                city=deal.location.get("city", ""),
                image_url=deal.image_url,
                end_date=deal.end_date,
                status=deal.status
            )
            for deal in deals
        ]

    except Exception as e:
        print(f"Get deals by category error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch deals: {str(e)}"
        )


# ============================================================================
# GET USER'S DEALS (NEW ENDPOINT)
# ============================================================================

@router.get("/user/my-deals", response_model=List[DealResponse])
async def get_my_deals(
    current_user_id: str = Depends(get_current_user),
    status_filter: Optional[DealStatus] = None
):
    """
    Get all deals created by the current user

    Returns all deals owned by the authenticated user.
    Requires authentication.
    """
    try:
        query = {"created_by": current_user_id}

        if status_filter:
            query["status"] = status_filter

        deals = await Deal.find(query).sort("-created_at").to_list()

        return [
            DealResponse(
                id=str(deal.id),
                title=deal.title,
                description=deal.description,
                original_price=deal.original_price,
                discounted_price=deal.discounted_price,
                discount_percentage=deal.discount_percentage,
                category=deal.category,
                tags=deal.tags,
                business_id=deal.business_id,
                business_name=deal.business_name,
                location=deal.location,
                start_date=deal.start_date,
                end_date=deal.end_date,
                status=deal.status,
                is_featured=deal.is_featured,
                image_url=deal.image_url,
                additional_images=deal.additional_images,
                views_count=deal.views_count,
                saves_count=deal.saves_count,
                terms=deal.terms,
                quantity_available=deal.quantity_available,
                created_at=deal.created_at,
                updated_at=deal.updated_at,
                created_by=deal.created_by
            )
            for deal in deals
        ]

    except Exception as e:
        print(f"Get my deals error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch your deals: {str(e)}"
        )