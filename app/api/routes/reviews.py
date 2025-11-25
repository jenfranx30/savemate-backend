"""
Reviews Routes for SaveMate API
Endpoints for creating, reading, updating reviews and ratings for deals
"""

from fastapi import APIRouter, HTTPException, status, Depends
from beanie import PydanticObjectId
from typing import List, Optional
from datetime import datetime

from app.models.review import Review
from app.models.deal import Deal
from app.models.business import Business
from app.schemas.review_schema import (
    ReviewCreate,
    ReviewUpdate,
    ReviewResponse,
    ReviewListResponse,
    ReviewHelpfulResponse
)
from app.core.security import get_current_user

router = APIRouter()


# ============================================================================
# CREATE REVIEW
# ============================================================================

@router.post("/", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    review_data: ReviewCreate,
    current_user_id: str = Depends(get_current_user)
):
    """
    Create a new review for a deal

    Users can review deals they've experienced.
    One review per user per deal.
    Requires authentication.
    """
    try:
        # Check if deal exists
        deal = await Deal.get(PydanticObjectId(review_data.deal_id))
        if not deal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deal not found"
            )

        # Check if user already reviewed this deal
        existing = await Review.find_one(
            Review.user_id == current_user_id,
            Review.deal_id == review_data.deal_id
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="You have already reviewed this deal. Use PUT to update your review."
            )

        # Validate rating
        if not (1 <= review_data.rating <= 5):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rating must be between 1 and 5"
            )

        # Create review
        new_review = Review(
            deal_id=review_data.deal_id,
            user_id=current_user_id,
            rating=review_data.rating,
            comment=review_data.comment,
            helpful_count=0
        )

        await new_review.insert()

        # Update business rating if deal has business_id
        if deal.business_id:
            try:
                business = await Business.get(PydanticObjectId(deal.business_id))
                if business:
                    await business.update_rating()
            except Exception as e:
                print(f"Warning: Could not update business rating: {str(e)}")

        return ReviewResponse(
            id=str(new_review.id),
            deal_id=new_review.deal_id,
            user_id=new_review.user_id,
            rating=new_review.rating,
            comment=new_review.comment,
            helpful_count=new_review.helpful_count,
            created_at=new_review.created_at,
            updated_at=new_review.updated_at
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Create review error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create review: {str(e)}"
        )


# ============================================================================
# GET DEAL REVIEWS
# ============================================================================

@router.get("/deal/{deal_id}", response_model=ReviewListResponse)
async def get_deal_reviews(
    deal_id: str,
    sort_by: str = "created_at",  # created_at, rating, helpful_count
    limit: int = 50
):
    """
    Get all reviews for a specific deal

    Returns reviews sorted by creation date, rating, or helpfulness.
    Public endpoint - no authentication required.
    """
    try:
        # Check if deal exists
        deal = await Deal.get(PydanticObjectId(deal_id))
        if not deal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deal not found"
            )

        # Determine sort field
        sort_field = "-created_at"  # Default: newest first
        if sort_by == "rating":
            sort_field = "-rating"
        elif sort_by == "helpful_count":
            sort_field = "-helpful_count"

        # Get reviews
        reviews = await Review.find(
            Review.deal_id == deal_id
        ).sort(sort_field).limit(limit).to_list()

        review_responses = [
            ReviewResponse(
                id=str(review.id),
                deal_id=review.deal_id,
                user_id=review.user_id,
                rating=review.rating,
                comment=review.comment,
                helpful_count=review.helpful_count,
                created_at=review.created_at,
                updated_at=review.updated_at
            )
            for review in reviews
        ]

        # Calculate average rating
        avg_rating = sum(r.rating for r in reviews) / len(reviews) if reviews else 0

        return ReviewListResponse(
            reviews=review_responses,
            total=len(reviews),
            average_rating=round(avg_rating, 2)
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Get deal reviews error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch reviews: {str(e)}"
        )


# ============================================================================
# GET USER REVIEWS
# ============================================================================

@router.get("/user/{user_id}", response_model=List[ReviewResponse])
async def get_user_reviews(user_id: str):
    """
    Get all reviews written by a specific user

    Returns reviews authored by the specified user.
    Public endpoint - no authentication required.
    """
    try:
        reviews = await Review.find(
            Review.user_id == user_id
        ).sort("-created_at").to_list()

        return [
            ReviewResponse(
                id=str(review.id),
                deal_id=review.deal_id,
                user_id=review.user_id,
                rating=review.rating,
                comment=review.comment,
                helpful_count=review.helpful_count,
                created_at=review.created_at,
                updated_at=review.updated_at
            )
            for review in reviews
        ]

    except Exception as e:
        print(f"Get user reviews error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch user reviews: {str(e)}"
        )


# ============================================================================
# GET MY REVIEWS (NEW ENDPOINT)
# ============================================================================

@router.get("/user/me/reviews", response_model=List[ReviewResponse])
async def get_my_reviews(
    current_user_id: str = Depends(get_current_user)
):
    """
    Get all reviews written by the current authenticated user

    Returns reviews authored by the logged-in user.
    Requires authentication.
    """
    try:
        reviews = await Review.find(
            Review.user_id == current_user_id
        ).sort("-created_at").to_list()

        return [
            ReviewResponse(
                id=str(review.id),
                deal_id=review.deal_id,
                user_id=review.user_id,
                rating=review.rating,
                comment=review.comment,
                helpful_count=review.helpful_count,
                created_at=review.created_at,
                updated_at=review.updated_at
            )
            for review in reviews
        ]

    except Exception as e:
        print(f"Get my reviews error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch your reviews: {str(e)}"
        )


# ============================================================================
# UPDATE REVIEW
# ============================================================================

@router.put("/{review_id}", response_model=ReviewResponse)
async def update_review(
    review_id: str,
    review_update: ReviewUpdate,
    current_user_id: str = Depends(get_current_user)
):
    """
    Update an existing review

    Only the review author can update their review.
    Requires authentication.
    """
    try:
        # Get review
        review = await Review.get(PydanticObjectId(review_id))

        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found"
            )

        # Check ownership
        if review.user_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update this review"
            )

        # Update fields
        update_data = review_update.dict(exclude_unset=True)

        # Validate rating if provided
        if "rating" in update_data:
            if not (1 <= update_data["rating"] <= 5):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Rating must be between 1 and 5"
                )

        # Update timestamp
        update_data["updated_at"] = datetime.utcnow()

        # Apply updates
        for field, value in update_data.items():
            setattr(review, field, value)

        await review.save()

        # Update business rating if rating changed
        if "rating" in update_data:
            deal = await Deal.get(PydanticObjectId(review.deal_id))
            if deal and deal.business_id:
                try:
                    business = await Business.get(PydanticObjectId(deal.business_id))
                    if business:
                        await business.update_rating()
                except Exception as e:
                    print(f"Warning: Could not update business rating: {str(e)}")

        return ReviewResponse(
            id=str(review.id),
            deal_id=review.deal_id,
            user_id=review.user_id,
            rating=review.rating,
            comment=review.comment,
            helpful_count=review.helpful_count,
            created_at=review.created_at,
            updated_at=review.updated_at
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Update review error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update review: {str(e)}"
        )


# ============================================================================
# DELETE REVIEW (NEW ENDPOINT)
# ============================================================================

@router.delete("/{review_id}", response_model=dict)
async def delete_review(
    review_id: str,
    current_user_id: str = Depends(get_current_user)
):
    """
    Delete a review

    Only the review author can delete their review.
    Requires authentication.
    """
    try:
        # Get review
        review = await Review.get(PydanticObjectId(review_id))

        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found"
            )

        # Check ownership
        if review.user_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to delete this review"
            )

        # Store deal_id before deletion for rating update
        deal_id = review.deal_id

        # Delete review
        await review.delete()

        # Update business rating
        deal = await Deal.get(PydanticObjectId(deal_id))
        if deal and deal.business_id:
            try:
                business = await Business.get(PydanticObjectId(deal.business_id))
                if business:
                    await business.update_rating()
            except Exception as e:
                print(f"Warning: Could not update business rating: {str(e)}")

        return {
            "message": "Review deleted successfully",
            "review_id": review_id
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Delete review error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete review: {str(e)}"
        )


# ============================================================================
# MARK REVIEW AS HELPFUL
# ============================================================================

@router.post("/{review_id}/helpful", response_model=ReviewHelpfulResponse)
async def mark_review_helpful(
    review_id: str,
    current_user_id: str = Depends(get_current_user)
):
    """
    Mark a review as helpful

    Users can vote reviews as helpful.
    Note: Currently allows multiple votes from same user.
    TODO: Implement vote tracking to prevent duplicate votes.
    Requires authentication.
    """
    try:
        # Get review
        review = await Review.get(PydanticObjectId(review_id))

        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found"
            )

        # TODO: Check if user already voted this review as helpful
        # This would require a new collection/model to track votes
        # For now, we'll allow multiple votes

        # Increment helpful count
        review.helpful_count += 1
        await review.save()

        return ReviewHelpfulResponse(
            review_id=review_id,
            helpful_count=review.helpful_count,
            message="Review marked as helpful"
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Mark helpful error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark review as helpful: {str(e)}"
        )


# ============================================================================
# GET REVIEW STATISTICS (NEW ENDPOINT)
# ============================================================================

@router.get("/stats/{deal_id}")
async def get_review_stats(deal_id: str):
    """
    Get review statistics for a deal

    Returns rating distribution and summary statistics.
    Public endpoint - no authentication required.
    """
    try:
        # Check if deal exists
        deal = await Deal.get(PydanticObjectId(deal_id))
        if not deal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deal not found"
            )

        # Get all reviews
        reviews = await Review.find(
            Review.deal_id == deal_id
        ).to_list()

        if not reviews:
            return {
                "total_reviews": 0,
                "average_rating": 0,
                "rating_distribution": {
                    "5": 0, "4": 0, "3": 0, "2": 0, "1": 0
                }
            }

        # Calculate statistics
        total = len(reviews)
        avg_rating = sum(r.rating for r in reviews) / total

        # Rating distribution
        distribution = {"5": 0, "4": 0, "3": 0, "2": 0, "1": 0}
        for review in reviews:
            distribution[str(review.rating)] += 1

        # Convert to percentages
        distribution_pct = {
            rating: round((count / total) * 100, 1)
            for rating, count in distribution.items()
        }

        return {
            "total_reviews": total,
            "average_rating": round(avg_rating, 2),
            "rating_distribution": distribution,
            "rating_distribution_percentage": distribution_pct,
            "most_common_rating": max(distribution, key=distribution.get)
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Get review stats error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch review statistics: {str(e)}"
        )