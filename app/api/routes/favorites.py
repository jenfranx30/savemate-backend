"""
Favorites Routes for SaveMate API
Endpoints for managing user favorite deals
"""

from fastapi import APIRouter, HTTPException, status
from beanie import PydanticObjectId
from datetime import datetime

from app.models.favorite import Favorite
from app.models.deal import Deal
from app.schemas.favorite_schema import (
    FavoriteCreate,
    FavoriteResponse,
    FavoriteWithDeal,
    FavoriteListResponse,
    FavoriteDeleteResponse,
    FavoriteCheckResponse
)

router = APIRouter()


@router.post("/", response_model=FavoriteResponse, status_code=status.HTTP_201_CREATED)
async def add_favorite(favorite_data: FavoriteCreate, current_user_id: str = "temp_user_id"):
    """Add a deal to favorites"""
    try:
        existing = await Favorite.find_one(
            Favorite.user_id == current_user_id,
            Favorite.deal_id == favorite_data.deal_id
        )
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Deal already in favorites"
            )
        
        deal = await Deal.get(PydanticObjectId(favorite_data.deal_id))
        if not deal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deal not found"
            )
        
        new_favorite = Favorite(
            user_id=current_user_id,
            deal_id=favorite_data.deal_id
        )
        
        await new_favorite.insert()
        await deal.increment_saves()
        
        return FavoriteResponse(
            id=str(new_favorite.id),
            user_id=new_favorite.user_id,
            deal_id=new_favorite.deal_id,
            created_at=new_favorite.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add favorite: {str(e)}"
        )


@router.delete("/{deal_id}", response_model=FavoriteDeleteResponse)
async def remove_favorite(deal_id: str, current_user_id: str = "temp_user_id"):
    """Remove a deal from favorites"""
    try:
        favorite = await Favorite.find_one(
            Favorite.user_id == current_user_id,
            Favorite.deal_id == deal_id
        )
        
        if not favorite:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Favorite not found"
            )
        
        await favorite.delete()
        
        return FavoriteDeleteResponse(
            message="Removed from favorites",
            deal_id=deal_id
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove favorite: {str(e)}"
        )


@router.get("/", response_model=FavoriteListResponse)
async def get_favorites(current_user_id: str = "temp_user_id"):
    """Get all user favorites"""
    try:
        favorites = await Favorite.find(Favorite.user_id == current_user_id).to_list()
        
        favorites_with_deals = []
        for fav in favorites:
            deal = await Deal.get(PydanticObjectId(fav.deal_id))
            if deal:
                favorites_with_deals.append(
                    FavoriteWithDeal(
                        id=str(fav.id),
                        user_id=fav.user_id,
                        deal_id=fav.deal_id,
                        created_at=fav.created_at,
                        deal={
                            "id": str(deal.id),
                            "title": deal.title,
                            "discounted_price": deal.discounted_price,
                            "discount_percentage": deal.discount_percentage,
                            "category": deal.category,
                            "business_name": deal.business_name,
                            "image_url": deal.image_url,
                            "status": deal.status,
                            "end_date": deal.end_date
                        }
                    )
                )
        
        return FavoriteListResponse(
            favorites=favorites_with_deals,
            total=len(favorites_with_deals)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch favorites: {str(e)}"
        )


@router.get("/check/{deal_id}", response_model=FavoriteCheckResponse)
async def check_favorite(deal_id: str, current_user_id: str = "temp_user_id"):
    """Check if a deal is favorited"""
    try:
        favorite = await Favorite.find_one(
            Favorite.user_id == current_user_id,
            Favorite.deal_id == deal_id
        )
        
        return FavoriteCheckResponse(
            is_favorited=favorite is not None,
            deal_id=deal_id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check favorite: {str(e)}"
        )
