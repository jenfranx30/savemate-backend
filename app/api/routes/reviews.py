"""
Reviews Routes for SaveMate API
Endpoints for managing deal reviews and ratings
"""

from fastapi import APIRouter, HTTPException, status
from beanie import PydanticObjectId
from datetime import datetime

from app.models.review import Review
from app.models.deal import Deal
from app.models.business import Business
from app.schemas.review_schema import (
    ReviewCreate,
    ReviewUpdate,
    ReviewResponse,
    ReviewListResponse,
    ReviewDeleteResponse,
    ReviewHelpfulResponse
)

router = APIRouter()


@router.post("/", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(review_data: ReviewCreate, current_user_id: str = "temp_user_id"):
    """Create a new review"""
    try:
        existing = await Review.find_one(
            Review.user_id == current_user_id,
            Review.deal_id == review_data.deal_id
        )
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already reviewed this deal"
            )
        
        deal = await Deal.get(PydanticObjectId(review_data.deal_id))
        if not deal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deal not found"
            )
        
        new_review = Review(
            deal_id=review_data.deal_id,
            user_id=current_user_id,
            business_id=deal.business_id,
            rating=review_data.rating,
            title=review_data.title,
            comment=review_data.comment
        )
        
        await new_review.insert()
        
        # Only update business rating if business_id is a valid ObjectId
        try:
            if len(deal.business_id) == 24:  # Valid ObjectId length
                business = await Business.get(PydanticObjectId(deal.business_id))
                if business:
                    await business.update_rating(float(review_data.rating))
        except:
            pass  # Skip business rating update if business_id is invalid

        return ReviewResponse(
            id=str(new_review.id),
            deal_id=new_review.deal_id,
            user_id=new_review.user_id,
            business_id=new_review.business_id,
            rating=new_review.rating,
            title=new_review.title,
            comment=new_review.comment,
            helpful_count=new_review.helpful_count,
            is_verified_purchase=new_review.is_verified_purchase,
            created_at=new_review.created_at,
            updated_at=new_review.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create review: {str(e)}"
        )


@router.get("/deal/{deal_id}", response_model=ReviewListResponse)
async def get_deal_reviews(deal_id: str):
    """Get all reviews for a specific deal"""
    try:
        reviews = await Review.find(Review.deal_id == deal_id).to_list()

        review_responses = [
            ReviewResponse(
                id=str(r.id),
                deal_id=r.deal_id,
                user_id=r.user_id,
                business_id=r.business_id,
                rating=r.rating,
                title=r.title,
                comment=r.comment,
                helpful_count=r.helpful_count,
                is_verified_purchase=r.is_verified_purchase,
                created_at=r.created_at,
                updated_at=r.updated_at
            )
            for r in reviews
        ]

        avg_rating = sum(r.rating for r in reviews) / len(reviews) if reviews else 0.0

        return ReviewListResponse(
            reviews=review_responses,
            total=len(reviews),
            average_rating=round(avg_rating, 2)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch reviews: {str(e)}"
        )


@router.get("/user/{user_id}", response_model=ReviewListResponse)
async def get_user_reviews(user_id: str):
    """Get all reviews by a specific user"""
    try:
        reviews = await Review.find(Review.user_id == user_id).to_list()

        review_responses = [
            ReviewResponse(
                id=str(r.id),
                deal_id=r.deal_id,
                user_id=r.user_id,
                business_id=r.business_id,
                rating=r.rating,
                title=r.title,
                comment=r.comment,
                helpful_count=r.helpful_count,
                is_verified_purchase=r.is_verified_purchase,
                created_at=r.created_at,
                updated_at=r.updated_at
            )
            for r in reviews
        ]

        avg_rating = sum(r.rating for r in reviews) / len(reviews) if reviews else 0.0

        return ReviewListResponse(
            reviews=review_responses,
            total=len(reviews),
            average_rating=round(avg_rating, 2)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch reviews: {str(e)}"
        )


@router.put("/{review_id}", response_model=ReviewResponse)
async def update_review(review_id: str, review_update: ReviewUpdate, current_user_id: str = "temp_user_id"):
    """Update a review"""
    try:
        review = await Review.get(PydanticObjectId(review_id))

        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found"
            )

        if review.user_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this review"
            )

        update_data = review_update.dict(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()

        for field, value in update_data.items():
            setattr(review, field, value)

        await review.save()

        return ReviewResponse(
            id=str(review.id),
            deal_id=review.deal_id,
            user_id=review.user_id,
            business_id=review.business_id,
            rating=review.rating,
            title=review.title,
            comment=review.comment,
            helpful_count=review.helpful_count,
            is_verified_purchase=review.is_verified_purchase,
            created_at=review.created_at,
            updated_at=review.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update review: {str(e)}"
        )


@router.post("/{review_id}/helpful", response_model=ReviewHelpfulResponse)
async def mark_review_helpful(review_id: str):
    """Mark a review as helpful"""
    try:
        review = await Review.get(PydanticObjectId(review_id))

        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found"
            )

        await review.increment_helpful()

        return ReviewHelpfulResponse(
            message="Marked as helpful",
            helpful_count=review.helpful_count
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark review as helpful: {str(e)}"
        )