"""
Business Routes for SaveMate API
Endpoints for creating, reading, updating, and deleting business profiles
"""

from fastapi import APIRouter, HTTPException, status, Query, Depends
from beanie import PydanticObjectId
from typing import Optional, List
from datetime import datetime

from app.models.business import Business, BusinessStatus, BusinessCategory
from app.schemas.business_schema import (
    BusinessCreate,
    BusinessUpdate,
    BusinessResponse,
    BusinessListResponse,
    BusinessDeleteResponse
)
from app.core.security import get_current_user

router = APIRouter()


# ============================================================================
# CREATE BUSINESS
# ============================================================================

@router.post("/", response_model=BusinessResponse, status_code=status.HTTP_201_CREATED)
async def create_business(
    business_data: BusinessCreate,
    current_user_id: str = Depends(get_current_user)
):
    """
    Create a new business profile

    Business owners can create their business profiles.
    Requires authentication.
    """
    try:
        # Check if user already has a business with this name
        existing = await Business.find_one(
            Business.owner_id == current_user_id,
            Business.name == business_data.name
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="You already have a business with this name"
            )

        # Create business instance
        new_business = Business(
            name=business_data.name,
            description=business_data.description,
            category=business_data.category,
            owner_id=current_user_id,
            contact_email=business_data.contact_email,
            contact_phone=business_data.contact_phone,
            website=business_data.website,
            location=business_data.location.dict() if business_data.location else None,
            operating_hours=business_data.operating_hours,
            logo_url=business_data.logo_url,
            cover_image_url=business_data.cover_image_url,
            social_media=business_data.social_media,
            verification_documents=business_data.verification_documents
        )

        # Save to database
        await new_business.insert()

        return BusinessResponse(
            id=str(new_business.id),
            name=new_business.name,
            description=new_business.description,
            category=new_business.category,
            owner_id=new_business.owner_id,
            contact_email=new_business.contact_email,
            contact_phone=new_business.contact_phone,
            website=new_business.website,
            location=new_business.location,
            operating_hours=new_business.operating_hours,
            logo_url=new_business.logo_url,
            cover_image_url=new_business.cover_image_url,
            social_media=new_business.social_media,
            average_rating=new_business.average_rating,
            total_reviews=new_business.total_reviews,
            total_deals=new_business.total_deals,
            is_verified=new_business.is_verified,
            verification_documents=new_business.verification_documents,
            status=new_business.status,
            created_at=new_business.created_at,
            updated_at=new_business.updated_at
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Create business error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create business: {str(e)}"
        )


# ============================================================================
# GET ALL BUSINESSES (WITH FILTERS)
# ============================================================================

@router.get("/", response_model=BusinessListResponse)
async def get_businesses(
    category: Optional[BusinessCategory] = None,
    city: Optional[str] = None,
    is_verified: Optional[bool] = None,
    min_rating: Optional[float] = Query(None, ge=0, le=5),
    search: Optional[str] = Query(None, min_length=2),
    status_filter: BusinessStatus = BusinessStatus.ACTIVE,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    sort_by: str = Query("created_at", pattern="^(created_at|name|average_rating|total_deals)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$")
):
    """
    Get all businesses with optional filtering

    Filter by category, location, rating, verification status, and more.
    Public endpoint - no authentication required.
    """
    try:
        # Build query
        query = {}

        # Status filter
        query["status"] = status_filter

        # Category filter
        if category:
            query["category"] = category

        # City filter
        if city:
            query["location.city"] = {"$regex": city, "$options": "i"}

        # Verification filter
        if is_verified is not None:
            query["is_verified"] = is_verified

        # Rating filter
        if min_rating:
            query["average_rating"] = {"$gte": min_rating}

        # Text search
        if search:
            query["$or"] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}},
                {"category": {"$regex": search, "$options": "i"}}
            ]

        # Get total count
        total = await Business.find(query).count()

        # Calculate pagination
        skip = (page - 1) * page_size
        total_pages = (total + page_size - 1) // page_size

        # Sort
        sort_direction = 1 if sort_order == "asc" else -1

        # Get businesses
        businesses = await Business.find(query).sort(
            (sort_by, sort_direction)
        ).skip(skip).limit(page_size).to_list()

        # Convert to response format
        business_responses = [
            BusinessResponse(
                id=str(business.id),
                name=business.name,
                description=business.description,
                category=business.category,
                owner_id=business.owner_id,
                contact_email=business.contact_email,
                contact_phone=business.contact_phone,
                website=business.website,
                location=business.location,
                operating_hours=business.operating_hours,
                logo_url=business.logo_url,
                cover_image_url=business.cover_image_url,
                social_media=business.social_media,
                average_rating=business.average_rating,
                total_reviews=business.total_reviews,
                total_deals=business.total_deals,
                is_verified=business.is_verified,
                verification_documents=business.verification_documents,
                status=business.status,
                created_at=business.created_at,
                updated_at=business.updated_at
            )
            for business in businesses
        ]

        return BusinessListResponse(
            businesses=business_responses,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )

    except Exception as e:
        print(f"Get businesses error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch businesses: {str(e)}"
        )


# ============================================================================
# GET BUSINESS BY ID
# ============================================================================

@router.get("/{business_id}", response_model=BusinessResponse)
async def get_business(business_id: str):
    """
    Get a specific business by ID

    Returns detailed business information.
    Public endpoint - no authentication required.
    """
    try:
        business = await Business.get(PydanticObjectId(business_id))

        if not business:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Business not found"
            )

        return BusinessResponse(
            id=str(business.id),
            name=business.name,
            description=business.description,
            category=business.category,
            owner_id=business.owner_id,
            contact_email=business.contact_email,
            contact_phone=business.contact_phone,
            website=business.website,
            location=business.location,
            operating_hours=business.operating_hours,
            logo_url=business.logo_url,
            cover_image_url=business.cover_image_url,
            social_media=business.social_media,
            average_rating=business.average_rating,
            total_reviews=business.total_reviews,
            total_deals=business.total_deals,
            is_verified=business.is_verified,
            verification_documents=business.verification_documents,
            status=business.status,
            created_at=business.created_at,
            updated_at=business.updated_at
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Get business error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch business: {str(e)}"
        )


# ============================================================================
# UPDATE BUSINESS
# ============================================================================

@router.put("/{business_id}", response_model=BusinessResponse)
async def update_business(
    business_id: str,
    business_update: BusinessUpdate,
    current_user_id: str = Depends(get_current_user)
):
    """
    Update an existing business

    Only the business owner can update their business.
    Requires authentication.
    """
    try:
        # Get business
        business = await Business.get(PydanticObjectId(business_id))

        if not business:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Business not found"
            )

        # Check ownership
        if business.owner_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update this business"
            )

        # Update fields
        update_data = business_update.dict(exclude_unset=True)

        # Update timestamp
        update_data["updated_at"] = datetime.utcnow()

        # Apply updates
        for field, value in update_data.items():
            setattr(business, field, value)

        # Save
        await business.save()

        return BusinessResponse(
            id=str(business.id),
            name=business.name,
            description=business.description,
            category=business.category,
            owner_id=business.owner_id,
            contact_email=business.contact_email,
            contact_phone=business.contact_phone,
            website=business.website,
            location=business.location,
            operating_hours=business.operating_hours,
            logo_url=business.logo_url,
            cover_image_url=business.cover_image_url,
            social_media=business.social_media,
            average_rating=business.average_rating,
            total_reviews=business.total_reviews,
            total_deals=business.total_deals,
            is_verified=business.is_verified,
            verification_documents=business.verification_documents,
            status=business.status,
            created_at=business.created_at,
            updated_at=business.updated_at
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Update business error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update business: {str(e)}"
        )


# ============================================================================
# DELETE BUSINESS
# ============================================================================

@router.delete("/{business_id}", response_model=BusinessDeleteResponse)
async def delete_business(
    business_id: str,
    current_user_id: str = Depends(get_current_user)
):
    """
    Delete a business

    Only the business owner can delete their business.
    Note: This will also affect related deals.
    Requires authentication.
    """
    try:
        # Get business
        business = await Business.get(PydanticObjectId(business_id))

        if not business:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Business not found"
            )

        # Check ownership
        if business.owner_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to delete this business"
            )

        # Optional: Check if business has active deals
        # from app.models.deal import Deal, DealStatus
        # active_deals = await Deal.find(
        #     Deal.business_id == business_id,
        #     Deal.status == DealStatus.ACTIVE
        # ).count()
        #
        # if active_deals > 0:
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST,
        #         detail=f"Cannot delete business with {active_deals} active deals. Please deactivate or remove deals first."
        #     )

        # Delete
        await business.delete()

        return BusinessDeleteResponse(
            message="Business deleted successfully",
            business_id=business_id
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Delete business error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete business: {str(e)}"
        )


# ============================================================================
# GET BUSINESSES BY OWNER
# ============================================================================

@router.get("/owner/{user_id}", response_model=List[BusinessResponse])
async def get_user_businesses(user_id: str):
    """
    Get all businesses owned by a specific user

    Returns list of businesses for the specified user.
    Public endpoint - no authentication required.
    """
    try:
        businesses = await Business.find(
            Business.owner_id == user_id
        ).sort("-created_at").to_list()

        return [
            BusinessResponse(
                id=str(business.id),
                name=business.name,
                description=business.description,
                category=business.category,
                owner_id=business.owner_id,
                contact_email=business.contact_email,
                contact_phone=business.contact_phone,
                website=business.website,
                location=business.location,
                operating_hours=business.operating_hours,
                logo_url=business.logo_url,
                cover_image_url=business.cover_image_url,
                social_media=business.social_media,
                average_rating=business.average_rating,
                total_reviews=business.total_reviews,
                total_deals=business.total_deals,
                is_verified=business.is_verified,
                verification_documents=business.verification_documents,
                status=business.status,
                created_at=business.created_at,
                updated_at=business.updated_at
            )
            for business in businesses
        ]

    except Exception as e:
        print(f"Get user businesses error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch user businesses: {str(e)}"
        )


# ============================================================================
# GET MY BUSINESSES (NEW ENDPOINT)
# ============================================================================

@router.get("/owner/me/businesses", response_model=List[BusinessResponse])
async def get_my_businesses(
    current_user_id: str = Depends(get_current_user)
):
    """
    Get all businesses owned by the current authenticated user

    Returns list of businesses for the logged-in user.
    Requires authentication.
    """
    try:
        businesses = await Business.find(
            Business.owner_id == current_user_id
        ).sort("-created_at").to_list()

        return [
            BusinessResponse(
                id=str(business.id),
                name=business.name,
                description=business.description,
                category=business.category,
                owner_id=business.owner_id,
                contact_email=business.contact_email,
                contact_phone=business.contact_phone,
                website=business.website,
                location=business.location,
                operating_hours=business.operating_hours,
                logo_url=business.logo_url,
                cover_image_url=business.cover_image_url,
                social_media=business.social_media,
                average_rating=business.average_rating,
                total_reviews=business.total_reviews,
                total_deals=business.total_deals,
                is_verified=business.is_verified,
                verification_documents=business.verification_documents,
                status=business.status,
                created_at=business.created_at,
                updated_at=business.updated_at
            )
            for business in businesses
        ]

    except Exception as e:
        print(f"Get my businesses error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch your businesses: {str(e)}"
        )


# ============================================================================
# GET BUSINESS DEALS
# ============================================================================

@router.get("/{business_id}/deals")
async def get_business_deals(business_id: str):
    """
    Get all deals for a specific business

    Returns list of deals associated with this business.
    Public endpoint - no authentication required.
    """
    try:
        from app.models.deal import Deal, DealStatus

        # Verify business exists
        business = await Business.get(PydanticObjectId(business_id))
        if not business:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Business not found"
            )

        # Get deals
        deals = await Deal.find(
            Deal.business_id == business_id,
            Deal.status == DealStatus.ACTIVE
        ).sort("-created_at").to_list()

        from app.schemas.deal_schema import DealResponse

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

    except HTTPException:
        raise
    except Exception as e:
        print(f"Get business deals error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch business deals: {str(e)}"
        )