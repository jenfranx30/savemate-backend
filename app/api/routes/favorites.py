"""
Favorites Routes for SaveMate API
Endpoints for managing user favorite deals (bookmarks)
"""

from fastapi import APIRouter, HTTPException, status, Depends
from beanie import PydanticObjectId
from typing import List
from datetime import datetime

from app.models.favorite import Favorite
from app.models.deal import Deal
from app.schemas.favorite_schema import (
    FavoriteCreate,
    FavoriteResponse,
    FavoriteListResponse,
    FavoriteDeleteResponse,
    FavoriteCheckResponse,
    FavoriteWithDeal
)
from app.core.security import get_current_user

router = APIRouter()


# ============================================================================
# ADD FAVORITE
# ============================================================================

@router.post("/", response_model=FavoriteResponse, status_code=status.HTTP_201_CREATED)
async def add_favorite(
    favorite_data: FavoriteCreate,
    current_user_id: str = Depends(get_current_user)
):
    """
    Add a deal to user's favorites

    Users can bookmark deals they're interested in.
    Requires authentication.
    """
    try:
        # Check if deal exists
        deal = await Deal.get(PydanticObjectId(favorite_data.deal_id))
        if not deal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deal not found"
            )

        # Check if already favorited
        existing = await Favorite.find_one(
            Favorite.user_id == current_user_id,
            Favorite.deal_id == favorite_data.deal_id
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Deal already in favorites"
            )

        # Create favorite
        new_favorite = Favorite(
            user_id=current_user_id,
            deal_id=favorite_data.deal_id
        )

        await new_favorite.insert()

        # Increment deal saves count
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
        print(f"Add favorite error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add favorite: {str(e)}"
        )


# ============================================================================
# REMOVE FAVORITE
# ============================================================================

@router.delete("/{deal_id}", response_model=FavoriteDeleteResponse)
async def remove_favorite(
    deal_id: str,
    current_user_id: str = Depends(get_current_user)
):
    """
    Remove a deal from user's favorites

    Users can remove bookmarked deals.
    Requires authentication.
    """
    try:
        # Find favorite
        favorite = await Favorite.find_one(
            Favorite.user_id == current_user_id,
            Favorite.deal_id == deal_id
        )

        if not favorite:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Favorite not found"
            )

        # Delete favorite
        await favorite.delete()

        # Decrement deal saves count
        deal = await Deal.get(PydanticObjectId(deal_id))
        if deal and deal.saves_count > 0:
            await deal.decrement_saves()

        return FavoriteDeleteResponse(
            message="Favorite removed successfully",
            deal_id=deal_id
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Remove favorite error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove favorite: {str(e)}"
        )


# ============================================================================
# GET USER FAVORITES
# ============================================================================

@router.get("/", response_model=FavoriteListResponse)
async def get_favorites(
    current_user_id: str = Depends(get_current_user)
):
    """
    Get all favorites for the current user

    Returns list of user's bookmarked deals with deal details.
    Requires authentication.
    """
    try:
        # Get all user favorites
        favorites = await Favorite.find(
            Favorite.user_id == current_user_id
        ).sort("-created_at").to_list()

        # Get deal details for each favorite
        favorites_with_deals = []

        for favorite in favorites:
            deal = await Deal.get(PydanticObjectId(favorite.deal_id))

            if deal:  # Only include if deal still exists
                from app.schemas.deal_schema import DealResponse

                favorites_with_deals.append(
                    FavoriteWithDeal(
                        id=str(favorite.id),
                        user_id=favorite.user_id,
                        deal_id=favorite.deal_id,
                        created_at=favorite.created_at,
                        deal=DealResponse(
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
                    )
                )

        return FavoriteListResponse(
            favorites=favorites_with_deals,
            total=len(favorites_with_deals)
        )

    except Exception as e:
        print(f"Get favorites error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch favorites: {str(e)}"
        )


# ============================================================================
# CHECK IF DEAL IS FAVORITED
# ============================================================================

@router.get("/check/{deal_id}", response_model=FavoriteCheckResponse)
async def check_favorite(
    deal_id: str,
    current_user_id: str = Depends(get_current_user)
):
    """
    Check if a deal is in user's favorites

    Returns whether the specified deal is bookmarked by the user.
    Requires authentication.
    """
    try:
        # Check if deal exists
        deal = await Deal.get(PydanticObjectId(deal_id))
        if not deal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deal not found"
            )

        # Check if favorited
        favorite = await Favorite.find_one(
            Favorite.user_id == current_user_id,
            Favorite.deal_id == deal_id
        )

        return FavoriteCheckResponse(
            deal_id=deal_id,
            is_favorited=favorite is not None,
            favorite_id=str(favorite.id) if favorite else None
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Check favorite error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check favorite: {str(e)}"
        )


# ============================================================================
# GET FAVORITE STATS (NEW ENDPOINT)
# ============================================================================

@router.get("/stats/summary")
async def get_favorite_stats(
    current_user_id: str = Depends(get_current_user)
):
    """
    Get statistics about user's favorites

    Returns summary information about bookmarked deals.
    Requires authentication.
    """
    try:
        # Get all favorites
        favorites = await Favorite.find(
            Favorite.user_id == current_user_id
        ).to_list()

        if not favorites:
            return {
                "total_favorites": 0,
                "categories": {},
                "average_discount": 0,
                "total_savings_potential": 0
            }

        # Aggregate stats
        categories = {}
        total_discount = 0
        total_savings = 0
        valid_deals = 0

        for favorite in favorites:
            deal = await Deal.get(PydanticObjectId(favorite.deal_id))
            if deal:
                valid_deals += 1

                # Count by category
                category = deal.category
                categories[category] = categories.get(category, 0) + 1

                # Calculate savings
                total_discount += deal.discount_percentage
                total_savings += (deal.original_price - deal.discounted_price)

        return {
            "total_favorites": len(favorites),
            "active_deals": valid_deals,
            "categories": categories,
            "average_discount": round(total_discount / valid_deals, 2) if valid_deals > 0 else 0,
            "total_savings_potential": round(total_savings, 2)
        }

    except Exception as e:
        print(f"Get favorite stats error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch favorite stats: {str(e)}"
        )


# ============================================================================
# CLEAR ALL FAVORITES (NEW ENDPOINT)
# ============================================================================

@router.delete("/clear/all", response_model=dict)
async def clear_all_favorites(
    current_user_id: str = Depends(get_current_user)
):
    """
    Remove all favorites for the current user

    Clears all bookmarked deals for the user.
    Requires authentication.
    """
    try:
        # Find all user favorites
        favorites = await Favorite.find(
            Favorite.user_id == current_user_id
        ).to_list()

        if not favorites:
            return {
                "message": "No favorites to clear",
                "removed_count": 0
            }

        # Delete all favorites
        removed_count = 0
        for favorite in favorites:
            await favorite.delete()

            # Decrement deal saves count
            deal = await Deal.get(PydanticObjectId(favorite.deal_id))
            if deal and deal.saves_count > 0:
                await deal.decrement_saves()

            removed_count += 1

        return {
            "message": f"Successfully cleared {removed_count} favorites",
            "removed_count": removed_count
        }

    except Exception as e:
        print(f"Clear favorites error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear favorites: {str(e)}"
        )