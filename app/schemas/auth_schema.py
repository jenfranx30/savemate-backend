"""
Authentication Schemas for SaveMate API

This module contains all Pydantic models for authentication-related requests and responses.
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime


# ============================================================================
# TOKEN MODELS
# ============================================================================

class Token(BaseModel):
    """
    Token model for authentication responses

    Contains both access and refresh tokens
    """
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }


class TokenResponse(BaseModel):
    """
    Response model for token refresh endpoint

    Returns new access and refresh tokens
    """
    access_token: str = Field(..., description="New JWT access token")
    refresh_token: str = Field(..., description="New JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }


class RefreshTokenRequest(BaseModel):
    """
    Request model for refresh token endpoint

    Requires a valid refresh token
    """
    refresh_token: str = Field(..., description="Valid JWT refresh token")

    class Config:
        json_schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }


# ============================================================================
# USER REQUEST MODELS
# ============================================================================

class UserLogin(BaseModel):
    """
    User login request schema

    Accepts either email or username along with password
    """
    email_or_username: str = Field(
        ...,
        min_length=3,
        description="User's email address or username"
    )
    password: str = Field(
        ...,
        min_length=8,
        description="User's password"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "email_or_username": "john.doe@example.com",
                "password": "SecurePass123!"
            }
        }


class UserRegister(BaseModel):
    """
    User registration request schema

    All fields are required for new user registration
    """
    email: EmailStr = Field(..., description="Valid email address")
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Unique username (3-50 characters)"
    )
    password: str = Field(
        ...,
        min_length=8,
        description="Password (minimum 8 characters)"
    )
    full_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="User's full name"
    )
    is_business_owner: bool = Field(
        default=False,
        description="Whether the user is registering as a business owner"
    )

    @validator('username')
    def username_alphanumeric(cls, v):
        """Validate that username contains only alphanumeric characters and underscores"""
        if not v.replace('_', '').isalnum():
            raise ValueError('Username must contain only letters, numbers, and underscores')
        return v.lower()

    @validator('email')
    def email_lowercase(cls, v):
        """Convert email to lowercase"""
        return v.lower()

    class Config:
        json_schema_extra = {
            "example": {
                "email": "john.doe@example.com",
                "username": "johndoe",
                "password": "SecurePass123!",
                "full_name": "John Doe",
                "is_business_owner": False
            }
        }


# ============================================================================
# USER RESPONSE MODELS
# ============================================================================

class UserResponse(BaseModel):
    """
    User response schema

    Returns safe user information (no sensitive data like passwords)
    """
    id: str = Field(..., description="User's unique identifier")
    email: str = Field(..., description="User's email address")
    username: str = Field(..., description="User's username")
    full_name: str = Field(..., description="User's full name")
    is_business_owner: bool = Field(..., description="Business owner status")
    created_at: Optional[datetime] = Field(None, description="Account creation timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "email": "john.doe@example.com",
                "username": "johndoe",
                "full_name": "John Doe",
                "is_business_owner": False,
                "created_at": "2025-11-22T12:00:00Z"
            }
        }


class AuthResponse(BaseModel):
    """
    Complete authentication response schema

    Returns success message, tokens, and user information
    """
    message: str = Field(..., description="Success message")
    tokens: Token = Field(..., description="Authentication tokens")
    user: UserResponse = Field(..., description="User information")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Login successful",
                "tokens": {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "token_type": "bearer"
                },
                "user": {
                    "id": "507f1f77bcf86cd799439011",
                    "email": "john.doe@example.com",
                    "username": "johndoe",
                    "full_name": "John Doe",
                    "is_business_owner": False
                }
            }
        }


# ============================================================================
# PASSWORD RESET MODELS (Optional - for future implementation)
# ============================================================================

class PasswordResetRequest(BaseModel):
    """
    Request model for password reset
    """
    email: EmailStr = Field(..., description="Email address for password reset")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "john.doe@example.com"
            }
        }


class PasswordResetConfirm(BaseModel):
    """
    Confirm password reset with new password
    """
    token: str = Field(..., description="Password reset token")
    new_password: str = Field(
        ...,
        min_length=8,
        description="New password (minimum 8 characters)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "token": "reset_token_here",
                "new_password": "NewSecurePass123!"
            }
        }


class PasswordChange(BaseModel):
    """
    Change password (when user is logged in)
    """
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(
        ...,
        min_length=8,
        description="New password (minimum 8 characters)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "current_password": "OldPass123!",
                "new_password": "NewSecurePass123!"
            }
        }


# ============================================================================
# ERROR RESPONSE MODELS
# ============================================================================

class ErrorDetail(BaseModel):
    """
    Error detail model
    """
    field: str = Field(..., description="Field that caused the error")
    message: str = Field(..., description="Error message")


class ErrorResponse(BaseModel):
    """
    Standard error response
    """
    success: bool = Field(default=False, description="Success status")
    message: str = Field(..., description="Error message")
    details: Optional[list[ErrorDetail]] = Field(
        None,
        description="Detailed error information"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "message": "Validation failed",
                "details": [
                    {
                        "field": "email",
                        "message": "Invalid email format"
                    }
                ]
            }
        }


class MessageResponse(BaseModel):
    """
    Simple message response
    """
    message: str = Field(..., description="Response message")
    success: bool = Field(default=True, description="Success status")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Operation completed successfully",
                "success": True
            }
        }