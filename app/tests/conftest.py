"""
Test Configuration for SaveMate Backend
"""

import pytest
import sys
import os
from datetime import datetime, timedelta

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


@pytest.fixture
async def client():
    """Create test client for API testing"""
    from httpx import AsyncClient, ASGITransport
    from app.main import app
    
    # Use ASGITransport to wrap the FastAPI app
    transport = ASGITransport(app=app)
    
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def test_user_id():
    """Mock user ID for testing"""
    return "674890abcdef123456789012"  # Valid MongoDB ObjectId format


@pytest.fixture
def auth_token(test_user_id):
    """Create authentication token"""
    try:
        from app.core.security import create_access_token
        token = create_access_token(data={"sub": test_user_id})
        return token
    except Exception as e:
        print(f"Warning: Could not create real token: {e}")
        return "mock_token_for_testing"


@pytest.fixture
def auth_headers(auth_token):
    """Create authorization headers"""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def sample_deal_data():
    """Sample deal data for testing"""
    return {
        "title": "Test Deal - 50% Off",
        "description": "This is a comprehensive test deal for automated testing purposes with sufficient length to meet requirements.",
        "original_price": 100.0,
        "discounted_price": 50.0,
        "category": "food",
        "business_name": "Test Business",
        "location": {
            "address": "Test Street 123",
            "city": "Warsaw",
            "postal_code": "00-001",
            "country": "Poland"
        },
        "end_date": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        "tags": ["test", "food"]
    }


@pytest.fixture
async def sample_deal(client, auth_headers, sample_deal_data):
    """Create a sample deal for testing (fixture)"""
    # Create a deal
    response = await client.post(
        "/api/v1/deals/",
        json=sample_deal_data,
        headers=auth_headers
    )
    
    if response.status_code == 201:
        deal = response.json()
        yield deal
        
        # Cleanup: delete the deal after test
        try:
            await client.delete(
                f"/api/v1/deals/{deal['id']}",
                headers=auth_headers
            )
        except:
            pass  # Ignore cleanup errors
    else:
        # If creation failed, yield None
        yield None


@pytest.fixture
async def test_business_user():
    """Mock business user for testing"""
    return {
        "id": "674890abcdef123456789012",
        "email": "business@test.com",
        "is_business": True
    }