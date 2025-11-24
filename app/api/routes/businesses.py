"""
Business Routes for SaveMate API
Endpoints for business profile management
"""

from fastapi import APIRouter, HTTPException, status, Query
from beanie import PydanticObjectId
from typing import Optional
from datetime import datetime

from app.models.business import Business, BusinessCategory, BusinessStatus
from app.models.deal import Deal
from app.schemas.business_schema import (
    BusinessCreate,
    BusinessUpdate,
    BusinessResponse,
    BusinessListResponse,
    BusinessDeleteResponse
)

router = APIRouter()


@router.post("/", response_model=BusinessResponse, status_code=status.HTTP_201_CREATED)
async def create_business(business_data: BusinessCreate, current_user_id: str = "temp_user_id"):
    """Create a new business profile"""
    try:
        new_business = Business(
            owner_id=current_user_id,
            business_name=business_data.business_name,
            description=business_data.description,
            category=business_data.category,
            email=business_data.email,
            phone=business_data.phone,
            website=business_data.website,
            location=business_data.location.dict(),
            logo_url=business_data.logo_url,
            cover_image_url=business_data.cover_image_url,
            images=business_data.images,
            operating_hours=business_data.operating_hours,
            tags=business_data.tags
        )
        
        await new_business.insert()
        
        return BusinessResponse(
            id=str(new_business.id),
            owner_id=new_business.owner_id,
            business_name=new_business.business_name,
            description=new_business.description,
            category=new_business.category,
            email=new_business.email,
            phone=new_business.phone,
            website=new_business.website,
            location=new_business.location,
            logo_url=new_business.logo_url,
            cover_image_url=new_business.cover_image_url,
            images=new_business.images,
            operating_hours=new_business.operating_hours,
            status=new_business.status,
            is_verified=new_business.is_verified,
            rating_average=new_business.rating_average,
            rating_count=new_business.rating_count,
            total_deals=new_business.total_deals,
            active_deals=new_business.active_deals,
            followers_count=new_business.followers_count,
            tags=new_business.tags,
            created_at=new_business.created_at,
            updated_at=new_business.updated_at
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create business: {str(e)}"
        )


@router.get("/", response_model=BusinessListResponse)
async def get_businesses(
    category: Optional[BusinessCategory] = None,
    city: Optional[str] = None,
    is_verified: Optional[bool] = None,
    status_filter: BusinessStatus = BusinessStatus.ACTIVE,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100)
):
    """Get all businesses with filters"""
    try:
        query = {"status": status_filter}
        
        if category:
            query["category"] = category
        
        if city:
            query["location.city"] = {"$regex": city, "$options": "i"}
        
        if is_verified is not None:
            query["is_verified"] = is_verified
        
        total = await Business.find(query).count()
        skip = (page - 1) * page_size
        total_pages = (total + page_size - 1) // page_size
        
        businesses = await Business.find(query).skip(skip).limit(page_size).to_list()
        
        business_responses = [
            BusinessResponse(
                id=str(b.id),
                owner_id=b.owner_id,
                business_name=b.business_name,
                description=b.description,
                category=b.category,
                email=b.email,
                phone=b.phone,
                website=b.website,
                location=b.location,
                logo_url=b.logo_url,
                cover_image_url=b.cover_image_url,
                images=b.images,
                operating_hours=b.operating_hours,
                status=b.status,
                is_verified=b.is_verified,
                rating_average=b.rating_average,
                rating_count=b.rating_count,
                total_deals=b.total_deals,
                active_deals=b.active_deals,
                followers_count=b.followers_count,
                tags=b.tags,
                created_at=b.created_at,
                updated_at=b.updated_at
            )
            for b in businesses
        ]
        
        return BusinessListResponse(
            businesses=business_responses,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch businesses: {str(e)}"
        )


@router.get("/{business_id}", response_model=BusinessResponse)
async def get_business(business_id: str):
    """Get a specific business by ID"""
    try:
        business = await Business.get(PydanticObjectId(business_id))
        
        if not business:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Business not found"
            )
        
        return BusinessResponse(
            id=str(business.id),
            owner_id=business.owner_id,
            business_name=business.business_name,
            description=business.description,
            category=business.category,
            email=business.email,
            phone=business.phone,
            website=business.website,
            location=business.location,
            logo_url=business.logo_url,
            cover_image_url=business.cover_image_url,
            images=business.images,
            operating_hours=business.operating_hours,
            status=business.status,
            is_verified=business.is_verified,
            rating_average=business.rating_average,
            rating_count=business.rating_count,
            total_deals=business.total_deals,
            active_deals=business.active_deals,
            followers_count=business.followers_count,
            tags=business.tags,
            created_at=business.created_at,
            updated_at=business.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch business: {str(e)}"
        )
"""
Business Routes (Part 2) - Update, Delete, Owner businesses, Business deals
Add this to the end of businesses.py after the get_business function
"""


@router.put("/{business_id}", response_model=BusinessResponse)
async def update_business(business_id: str, business_update: BusinessUpdate, current_user_id: str = "temp_user_id"):
    """Update a business"""
    try:
        business = await Business.get(PydanticObjectId(business_id))
        
        if not business:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Business not found"
            )
        
        update_data = business_update.dict(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()
        
        for field, value in update_data.items():
            setattr(business, field, value)
        
        await business.save()
        
        return BusinessResponse(
            id=str(business.id),
            owner_id=business.owner_id,
            business_name=business.business_name,
            description=business.description,
            category=business.category,
            email=business.email,
            phone=business.phone,
            website=business.website,
            location=business.location,
            logo_url=business.logo_url,
            cover_image_url=business.cover_image_url,
            images=business.images,
            operating_hours=business.operating_hours,
            status=business.status,
            is_verified=business.is_verified,
            rating_average=business.rating_average,
            rating_count=business.rating_count,
            total_deals=business.total_deals,
            active_deals=business.active_deals,
            followers_count=business.followers_count,
            tags=business.tags,
            created_at=business.created_at,
            updated_at=business.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update business: {str(e)}"
        )


@router.delete("/{business_id}", response_model=BusinessDeleteResponse)
async def delete_business(business_id: str, current_user_id: str = "temp_user_id"):
    """Delete a business"""
    try:
        business = await Business.get(PydanticObjectId(business_id))
        
        if not business:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Business not found"
            )
        
        await business.delete()
        
        return BusinessDeleteResponse(
            message="Business deleted successfully",
            business_id=business_id
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete business: {str(e)}"
        )


@router.get("/owner/{user_id}", response_model=BusinessListResponse)
async def get_user_businesses(user_id: str):
    """Get all businesses owned by a user"""
    try:
        businesses = await Business.find(Business.owner_id == user_id).to_list()
        
        business_responses = [
            BusinessResponse(
                id=str(b.id),
                owner_id=b.owner_id,
                business_name=b.business_name,
                description=b.description,
                category=b.category,
                email=b.email,
                phone=b.phone,
                website=b.website,
                location=b.location,
                logo_url=b.logo_url,
                cover_image_url=b.cover_image_url,
                images=b.images,
                operating_hours=b.operating_hours,
                status=b.status,
                is_verified=b.is_verified,
                rating_average=b.rating_average,
                rating_count=b.rating_count,
                total_deals=b.total_deals,
                active_deals=b.active_deals,
                followers_count=b.followers_count,
                tags=b.tags,
                created_at=b.created_at,
                updated_at=b.updated_at
            )
            for b in businesses
        ]
        
        return BusinessListResponse(
            businesses=business_responses,
            total=len(businesses),
            page=1,
            page_size=len(businesses),
            total_pages=1
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch businesses: {str(e)}"
        )


@router.get("/{business_id}/deals")
async def get_business_deals(business_id: str):
    """Get all deals from a specific business"""
    try:
        deals = await Deal.find(Deal.business_id == business_id).to_list()
        
        return {
            "business_id": business_id,
            "deals": [
                {
                    "id": str(d.id),
                    "title": d.title,
                    "discounted_price": d.discounted_price,
                    "discount_percentage": d.discount_percentage,
                    "status": d.status,
                    "end_date": d.end_date
                }
                for d in deals
            ],
            "total": len(deals)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch deals: {str(e)}"
        )
