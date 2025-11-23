"""
Minimal User Model - NO PASSWORD HASHING ANYWHERE
SaveMate API - MongoDB/Beanie
"""

from beanie import Document
from datetime import datetime


class User(Document):
    """
    User document - CRITICAL: password_hash is ALREADY hashed!
    Do NOT add ANY validators, @before_event, or properties that touch password_hash!
    """
    email: str
    username: str
    password_hash: str  # ALREADY HASHED - DO NOT TOUCH
    full_name: str
    is_business_owner: bool = False
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime = datetime.utcnow()

    class Settings:
        name = "users"
        indexes = ["email", "username"]

# NO @before_event
# NO @validator
# NO properties
# NO __init__ override
# NOTHING that touches password_hash!