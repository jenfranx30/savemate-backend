"""
Security utilities for SaveMate API

This module contains functions for password hashing, JWT token generation and verification,
and authentication dependencies.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from beanie import PydanticObjectId
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings from environment variables
SECRET_KEY = os.getenv("JWT_SECRET", "your-secret-key-change-this-in-production")
REFRESH_SECRET_KEY = os.getenv("JWT_REFRESH_SECRET", "your-refresh-secret-key-change-this")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# Security scheme for FastAPI
security = HTTPBearer()


# ============================================================================
# PASSWORD HASHING FUNCTIONS
# ============================================================================

def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt

    Args:
        password: Plain text password

    Returns:
        Hashed password string
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash

    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to compare against

    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


# ============================================================================
# JWT TOKEN FUNCTIONS
# ============================================================================

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token

    Args:
        data: Data to encode in the token (usually {"sub": user_id})
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def create_refresh_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT refresh token

    Args:
        data: Data to encode in the token (usually {"sub": user_id})
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT refresh token string
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def verify_access_token(token: str) -> Dict[str, Any]:
    """
    Verify and decode an access token

    Args:
        token: JWT access token to verify

    Returns:
        Decoded token payload

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Check token type
        token_type = payload.get("type")
        if token_type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return payload

    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


def verify_refresh_token(token: str) -> Dict[str, Any]:
    """
    Verify and decode a refresh token

    Args:
        token: JWT refresh token to verify

    Returns:
        Decoded token payload

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])

        # Check token type
        token_type = payload.get("type")
        if token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type - expected refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return payload

    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid refresh token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


def decode_token(token: str, secret_key: str = SECRET_KEY) -> Dict[str, Any]:
    """
    Decode a JWT token without verification (use carefully!)

    Args:
        token: JWT token to decode
        secret_key: Secret key to use for decoding

    Returns:
        Decoded token payload

    Raises:
        JWTError: If token cannot be decoded
    """
    try:
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise JWTError(f"Could not decode token: {str(e)}")


# ============================================================================
# AUTHENTICATION DEPENDENCY
# ============================================================================

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    FastAPI dependency to get current authenticated user

    Extracts JWT token from Authorization header, validates it,
    and returns the user ID.

    Args:
        credentials: HTTP Bearer token from Authorization header

    Returns:
        User ID string from token

    Raises:
        HTTPException 401: If token is invalid, expired, or missing
        HTTPException 404: If user not found in database (optional check)

    Usage in routes:
        @router.post("/protected")
        async def protected_route(current_user_id: str = Depends(get_current_user)):
            # Use current_user_id here
            pass
    """
    token = credentials.credentials

    try:
        # Verify and decode token
        payload = verify_access_token(token)
        user_id: str = payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User ID not found in token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Optional: Verify user exists in database
        # Uncomment if you want to check user existence on every request
        # from app.models.user import User
        # try:
        #     user = await User.get(PydanticObjectId(user_id))
        #     if not user:
        #         raise HTTPException(
        #             status_code=status.HTTP_404_NOT_FOUND,
        #             detail="User not found"
        #         )
        #     if not user.is_active:
        #         raise HTTPException(
        #             status_code=status.HTTP_403_FORBIDDEN,
        #             detail="User account is inactive"
        #         )
        # except Exception as e:
        #     raise HTTPException(
        #         status_code=status.HTTP_404_NOT_FOUND,
        #         detail=f"User not found: {str(e)}"
        #     )

        return user_id

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_active_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    FastAPI dependency to get current authenticated user with full user data

    Similar to get_current_user but returns the full user object from database.
    Use this when you need user information beyond just the ID.

    Args:
        credentials: HTTP Bearer token from Authorization header

    Returns:
        User object from database

    Raises:
        HTTPException: If token is invalid or user not found
    """
    from app.models.user import User

    token = credentials.credentials

    try:
        payload = verify_access_token(token)
        user_id: str = payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User ID not found in token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Get user from database
        user = await User.get(PydanticObjectId(user_id))

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )

        return user

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ============================================================================
# TOKEN EXTRACTION HELPERS
# ============================================================================

def get_user_id_from_token(token: str) -> str:
    """
    Extract user ID from an access token

    Args:
        token: JWT access token

    Returns:
        User ID string

    Raises:
        HTTPException: If token is invalid or user ID not found
    """
    payload = verify_access_token(token)
    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID not found in token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_id


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validate password strength

    Args:
        password: Password to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    if not any(char.isdigit() for char in password):
        return False, "Password must contain at least one digit"

    if not any(char.isupper() for char in password):
        return False, "Password must contain at least one uppercase letter"

    if not any(char.islower() for char in password):
        return False, "Password must contain at least one lowercase letter"

    # Optional: Check for special characters
    # special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    # if not any(char in special_chars for char in password):
    #     return False, "Password must contain at least one special character"

    return True, ""


def create_token_pair(user_id: str) -> Dict[str, str]:
    """
    Create both access and refresh tokens for a user

    Args:
        user_id: User's unique identifier

    Returns:
        Dictionary with access_token and refresh_token
    """
    access_token = create_access_token(data={"sub": user_id})
    refresh_token = create_refresh_token(data={"sub": user_id})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


# ============================================================================
# CONFIGURATION INFO (for debugging)
# ============================================================================

def get_security_config_info() -> Dict[str, Any]:
    """
    Get current security configuration (for debugging only)

    Returns:
        Dictionary with configuration information
    """
    return {
        "algorithm": ALGORITHM,
        "access_token_expire_minutes": ACCESS_TOKEN_EXPIRE_MINUTES,
        "refresh_token_expire_days": REFRESH_TOKEN_EXPIRE_DAYS,
        "secret_key_configured": bool(SECRET_KEY and SECRET_KEY != "your-secret-key-change-this-in-production"),
        "refresh_secret_configured": bool(REFRESH_SECRET_KEY and REFRESH_SECRET_KEY != "your-refresh-secret-key-change-this")
    }


if __name__ == "__main__":
    # Test the module
    print("Security module loaded successfully!")
    print(f"Configuration: {get_security_config_info()}")

    # Test password hashing
    test_password = "TestPassword123"
    hashed = hash_password(test_password)
    print(f"\nPassword hashing test:")
    print(f"Original: {test_password}")
    print(f"Hashed: {hashed}")
    print(f"Verification: {verify_password(test_password, hashed)}")

    # Test token creation
    test_user_id = "test_user_123"
    tokens = create_token_pair(test_user_id)
    print(f"\nToken creation test:")
    print(f"Access token: {tokens['access_token'][:50]}...")
    print(f"Refresh token: {tokens['refresh_token'][:50]}...")