"""
Authentication routes for SaveMate API

This module handles user registration, login, and token refresh for MongoDB.
"""

from fastapi import APIRouter, HTTPException, status
from beanie import PydanticObjectId
from typing import Optional

from app.models.user import User
from app.schemas.auth_schema import (
    UserLogin,
    UserRegister,
    AuthResponse,
    Token,
    TokenResponse,
    RefreshTokenRequest,
    UserResponse
)
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_refresh_token
)

# Create router instance
router = APIRouter()


# ============================================================================
# REGISTRATION ENDPOINT
# ============================================================================

@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister):
    """
    Register a new user

    Creates a new user account with hashed password and returns authentication tokens.

    Args:
        user_data: User registration data (email, username, password, etc.)

    Returns:
        AuthResponse with tokens and user information

    Raises:
        HTTPException: If email or username already exists
    """
    try:
        # Check if email already exists
        existing_email = await User.find_one(User.email == user_data.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists"
            )

        # Check if username already exists
        existing_username = await User.find_one(User.username == user_data.username)
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already taken"
            )

        # Hash the password
        hashed_password = hash_password(user_data.password)

        # Create new user
        new_user = User(
            email=user_data.email,
            username=user_data.username,
            password_hash=hashed_password,
            full_name=user_data.full_name,
            is_business_owner=user_data.is_business_owner
        )

        # Save to database
        await new_user.insert()

        # Generate tokens
        access_token = create_access_token(data={"sub": str(new_user.id)})
        refresh_token = create_refresh_token(data={"sub": str(new_user.id)})

        tokens = Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )

        user_response = UserResponse(
            id=str(new_user.id),
            email=new_user.email,
            username=new_user.username,
            full_name=new_user.full_name,
            is_business_owner=new_user.is_business_owner,
            created_at=new_user.created_at if hasattr(new_user, 'created_at') else None
        )

        return AuthResponse(
            message="User registered successfully",
            tokens=tokens,
            user=user_response
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


# ============================================================================
# LOGIN ENDPOINT
# ============================================================================

@router.post("/login", response_model=AuthResponse)
async def login(credentials: UserLogin):
    """
    Login user with email/username and password

    Authenticates user and returns JWT tokens.

    Args:
        credentials: Login credentials (email_or_username, password)

    Returns:
        AuthResponse with tokens and user information

    Raises:
        HTTPException: If credentials are invalid
    """
    try:
        # MongoDB query - find user by email OR username
        user = await User.find_one({
            "$or": [
                {"email": credentials.email_or_username},
                {"username": credentials.email_or_username}
            ]
        })

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email/username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Verify password
        if not verify_password(credentials.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email/username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Generate tokens
        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})

        tokens = Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )

        user_response = UserResponse(
            id=str(user.id),
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            is_business_owner=user.is_business_owner,
            created_at=user.created_at if hasattr(user, 'created_at') else None
        )

        return AuthResponse(
            message="Login successful",
            tokens=tokens,
            user=user_response
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )


# ============================================================================
# REFRESH TOKEN ENDPOINT
# ============================================================================

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(token_data: RefreshTokenRequest):
    """
    Refresh access token using refresh token

    Generates new access and refresh tokens from a valid refresh token.

    Args:
        token_data: Refresh token request with refresh_token

    Returns:
        TokenResponse with new tokens

    Raises:
        HTTPException: If refresh token is invalid or user not found
    """
    try:
        # Verify refresh token
        payload = verify_refresh_token(token_data.refresh_token)
        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token - user ID not found"
            )

        # Find user by ID (MongoDB query)
        try:
            user = await User.get(PydanticObjectId(user_id))
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )

        # Generate new tokens
        new_access_token = create_access_token(data={"sub": str(user.id)})
        new_refresh_token = create_refresh_token(data={"sub": str(user.id)})

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer"
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Refresh token error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )


# ============================================================================
# OPTIONAL: LOGOUT ENDPOINT (Token Blacklisting)
# ============================================================================

# Note: Since JWTs are stateless, true logout requires token blacklisting
# This is a placeholder for future implementation

@router.post("/logout")
async def logout():
    """
    Logout user (placeholder)

    In a production app, this would add the token to a blacklist.
    For now, clients should just discard the tokens.

    Returns:
        Success message
    """
    return {
        "message": "Logout successful. Please discard your tokens on the client side.",
        "success": True
    }

# ============================================================================
# OPTIONAL: GET CURRENT USER ENDPOINT
# ============================================================================

# This would require authentication middleware - can be added later
# Example:
# @router.get("/me", response_model=UserResponse)
# async def get_current_user(current_user: User = Depends(get_current_user)):
#     """Get current authenticated user"""
#     return UserResponse(
#         id=str(current_user.id),
#         email=current_user.email,
#         username=current_user.username,
#         full_name=current_user.full_name,
#         is_business_owner=current_user.is_business_owner
#     )