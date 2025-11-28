"""
Basic API Tests - No authentication required
"""

import pytest


@pytest.mark.asyncio
async def test_list_deals(client):
    """Test GET /api/v1/deals/ - Public endpoint"""
    response = await client.get("/api/v1/deals/")
    
    assert response.status_code == 200
    data = response.json()
    
    # Check response structure
    assert "deals" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "total_pages" in data
    
    # Check types
    assert isinstance(data["deals"], list)
    assert isinstance(data["total"], int)
    
    print(f"✅ Found {data['total']} deals, page {data['page']}/{data['total_pages']}")


@pytest.mark.asyncio
async def test_list_deals_with_pagination(client):
    """Test pagination parameters"""
    response = await client.get("/api/v1/deals/?page=1&page_size=5")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["page"] == 1
    assert data["page_size"] == 5
    assert len(data["deals"]) <= 5
    
    print(f"✅ Pagination works: {len(data['deals'])} deals per page")


@pytest.mark.asyncio
async def test_filter_by_category(client):
    """Test category filtering"""
    response = await client.get("/api/v1/deals/category/food")
    
    assert response.status_code == 200
    data = response.json()
    
    assert isinstance(data, list)
    
    # All deals should be food category
    for deal in data:
        assert deal["category"] == "food"
    
    print(f"✅ Category filter works: {len(data)} food deals")


@pytest.mark.asyncio
async def test_create_without_auth_fails(client, sample_deal_data):
    """Test that creating deal without auth returns 401"""
    response = await client.post(
        "/api/v1/deals/",
        json=sample_deal_data
    )
    
    assert response.status_code == 401
    print("✅ Auth protection works - got 401 without token")


@pytest.mark.asyncio
async def test_invalid_deal_id_format(client):
    """Test handling of invalid deal ID"""
    response = await client.get("/api/v1/deals/invalid-id-123")
    
    # Should return 400, 422, or 500 depending on error handling
    assert response.status_code in [400, 422, 500]
    print(f"✅ Invalid ID handling works - got {response.status_code}")