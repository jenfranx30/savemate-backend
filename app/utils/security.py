"""
Security utilities for password hashing, JWT tokens, and authentication
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.config import settings
from app.models.user import User


# ============================================================================
# PASSWORD HASHING
# ============================================================================

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password
    
    Args:
        plain_password: The plain text password
        hashed_password: The hashed password from database
    
    Returns:
        bool: True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt
    
    Args:
        password: Plain text password
    
    Returns:
        str: Hashed password
    """
    return pwd_context.hash(password)


# ============================================================================
# JWT TOKEN CREATION
# ============================================================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token
    
    Args:
        data: Data to encode in the token (usually {"sub": user_id})
        expires_delta: Optional custom expiration time
    
    Returns:
        str: Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """
    Create a JWT refresh token
    
    Args:
        data: Data to encode in the token (usually {"sub": user_id})
    
    Returns:
        str: Encoded JWT refresh token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


# ============================================================================
# JWT TOKEN DECODING
# ============================================================================

def decode_token(token: str) -> Optional[dict]:
    """
    Decode and verify a JWT token
    
    Args:
        token: JWT token to decode
    
    Returns:
        dict: Decoded token payload or None if invalid
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


# ============================================================================
# AUTHENTICATION DEPENDENCIES
# ============================================================================

# HTTP Bearer token scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """
    Get the current authenticated user from JWT token
    
    Args:
        credentials: HTTP Bearer credentials from request header
    
    Returns:
        User: The authenticated user object
    
    Raises:
        HTTPException: 401 if token is invalid or user not found
    """
    # Extract token
    token = credentials.credentials
    
    # Decode token
    payload = decode_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract user ID from token
    user_id: str = payload.get("sub")
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    user = await User.get(user_id)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def require_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Require admin role for protected endpoints
    
    This dependency checks if the authenticated user has admin privileges.
    Use this for endpoints that should only be accessible to administrators.
    
    Usage:
        @router.post("/admin-only-endpoint")
        async def admin_endpoint(current_user: User = Depends(require_admin)):
            # Only admins can access this
            pass
    
    Args:
        current_user: The authenticated user (injected by get_current_user)
    
    Returns:
        User: The authenticated admin user
    
    Raises:
        HTTPException: 403 if user is not an admin
    """
    # Option 1: Check if user has 'is_admin' field
    if not getattr(current_user, 'is_admin', False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required. You don't have permission to perform this action."
        )
    
    # Option 2: Check if user has 'role' field set to 'admin'
    # Uncomment this if you use role-based system instead of is_admin flag
    # user_role = getattr(current_user, 'role', None)
    # if user_role != 'admin':
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Admin access required. You don't have permission to perform this action."
    #     )
    
    # Option 3: Check if user is a business owner (for business-specific admin actions)
    # Uncomment this if business owners should have admin access
    # if not getattr(current_user, 'is_business', False):
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Business account required. You don't have permission to perform this action."
    #     )
    
    return current_user


async def require_business(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Require business account for protected endpoints
    
    Use this for endpoints that should only be accessible to business accounts
    (e.g., creating deals, managing business profile)
    
    Args:
        current_user: The authenticated user (injected by get_current_user)
    
    Returns:
        User: The authenticated business user
    
    Raises:
        HTTPException: 403 if user is not a business account
    """
    if not getattr(current_user, 'is_business', False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Business account required. Please upgrade to a business account to access this feature."
        )
    
    return current_user


# ============================================================================
# TEMPORARY TESTING HELPER (Remove in production)
# ============================================================================

async def require_admin_temp(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    TEMPORARY: Allow any authenticated user to act as admin
    
    ⚠️ WARNING: This is for testing/development only!
    Use this temporarily if your User model doesn't have is_admin field yet.
    
    Replace with proper require_admin once User model is updated.
    
    Args:
        current_user: The authenticated user
    
    Returns:
        User: The authenticated user (treated as admin)
    """
    # TODO: Remove this function and use require_admin instead
    return current_user


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def create_tokens_for_user(user_id: str) -> dict:
    """
    Create both access and refresh tokens for a user
    
    Convenience function to create both tokens at once (e.g., during login)
    
    Args:
        user_id: The user's ID
    
    Returns:
        dict: Dictionary with 'access_token' and 'refresh_token'
    """
    access_token = create_access_token(data={"sub": user_id})
    refresh_token = create_refresh_token(data={"sub": user_id})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


def verify_token_type(token: str, expected_type: str) -> bool:
    """
    Verify that a token is of the expected type (access or refresh)
    
    Args:
        token: JWT token to verify
        expected_type: Expected token type ("access" or "refresh")
    
    Returns:
        bool: True if token type matches, False otherwise
    """
    payload = decode_token(token)
    
    if payload is None:
        return False
    
    token_type = payload.get("type")
    return token_type == expected_type


# ============================================================================
# NOTES FOR USER MODEL
# ============================================================================

"""
To use require_admin, your User model needs one of these fields:

Option 1 - Boolean flag (RECOMMENDED):
    class User(Document):
        # ... other fields ...
        is_admin: bool = Field(
            default=False,
            description="Whether user has admin privileges"
        )

Option 2 - Role-based:
    class User(Document):
        # ... other fields ...
        role: str = Field(
            default="user",
            description="User role: 'user', 'business', or 'admin'"
        )

Option 3 - Business flag (for business admin):
    class User(Document):
        # ... other fields ...
        is_business: bool = Field(
            default=False,
            description="Whether user is a business account"
        )

Choose Option 1 for simplest implementation!
"""