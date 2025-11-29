"""
Minimal User Model - NO PASSWORD HASHING ANYWHERE
SaveMate API - MongoDB/Beanie
"""

from beanie import Document
from pydantic import Field, EmailStr
from datetime import datetime
from typing import Optional

class User(Document):
    email: EmailStr = Field(..., unique=True)
    username: str = Field(..., unique=True)
    password_hash: str
    full_name: Optional[str] = None
    is_business_owner: bool = Field(default=False)
    
    # ADD THIS FIELD ⬇️
    is_admin: bool = Field(
        default=False,
        description="Admin privileges for managing categories and system settings"
    )
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "users"
        indexes = ["email", "username"]