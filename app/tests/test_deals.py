"""
Comprehensive Test Suite for Deals API
Tests all CRUD operations, authentication, authorization, and validation
"""

import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta
from beanie import PydanticObjectId

# Assuming your app structure
# from app.main import app
# from app.models.deal import Deal, DealCategory, DealStatus
# from app.models.user import User
# from app.core.security import create_access_token


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
async def async_client():
    """Create async HTTP client for testing"""
    from app.main import app
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
async def test_user():
    """Create a test user for authentication"""
    from app.models.user import User
    
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="$2b$12$...",  # Mock hashed password
        is_active=True
    )
    await user.insert()
    yield user
    await user.delete()


@pytest.fixture
async def test_business_user():
    """Create a test business user"""
    from app.models.user import User
    
    user = User(
        email="business@example.com",
        username="businessuser",
        hashed_password="$2b$12$...",
        is_business=True,
        business_id="test_business_123",
        is_active=True
    )
    await user.insert()
    yield user
    await user.delete()


@pytest.fixture
def auth_token(test_business_user):
    """Create authentication token for test user"""
    from app.core.security import create_access_token
    
    token = create_access_token(
        data={"sub": str(test_business_user.id)}
    )
    return token


@pytest.fixture
def auth_headers(auth_token):
    """Create authorization headers"""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
async def sample_deal(test_business_user):
    """Create a sample deal for testing"""
    from app.models.deal import Deal, DealCategory, DealStatus
    
    deal = Deal(
        title="Test Deal - 50% Off",
        description="This is a test deal for automated testing purposes.",
        original_price=100.0,
        discounted_price=50.0,
        discount_percentage=50,
        category=DealCategory.FOOD,
        tags=["test", "food"],
        business_id=str(test_business_user.id),
        business_name="Test Business",
        location={
            "address": "Test Street 123",
            "city": "Warsaw",
            "postal_code": "00-001",
            "country": "Poland"
        },
        start_date=datetime.utcnow(),
        end_date=datetime.utcnow() + timedelta(days=30),
        status=DealStatus.ACTIVE,
        created_by=str(test_business_user.id)
    )
    await deal.insert()
    yield deal
    await deal.delete()


# ============================================================================
# TEST: CREATE DEAL (POST /api/v1/deals/)
# ============================================================================

class TestCreateDeal:
    """Test suite for creating deals"""

    @pytest.mark.asyncio
    async def test_create_deal_success(self, async_client, auth_headers):
        """Test successful deal creation"""
        deal_data = {
            "title": "New Test Deal",
            "description": "A brand new test deal with detailed description that meets minimum length.",
            "original_price": 150.0,
            "discounted_price": 75.0,
            "category": "food",
            "business_name": "My Test Business",
            "location": {
                "address": "Test St 456",
                "city": "Warsaw",
                "postal_code": "00-002",
                "country": "Poland"
            },
            "end_date": (datetime.utcnow() + timedelta(days=15)).isoformat(),
            "tags": ["test", "new"]
        }

        response = await async_client.post(
            "/api/v1/deals/",
            json=deal_data,
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == deal_data["title"]
        assert data["discount_percentage"] == 50
        assert "id" in data

    @pytest.mark.asyncio
    async def test_create_deal_without_auth(self, async_client):
        """Test that creating deal without auth fails"""
        deal_data = {
            "title": "Unauthorized Deal",
            "description": "This should fail because no authentication token provided.",
            "original_price": 100.0,
            "discounted_price": 50.0,
            "category": "food",
            "business_name": "Test Business",
            "location": {"city": "Warsaw"},
            "end_date": (datetime.utcnow() + timedelta(days=10)).isoformat()
        }

        response = await async_client.post(
            "/api/v1/deals/",
            json=deal_data
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_create_deal_invalid_title_too_short(self, async_client, auth_headers):
        """Test validation: title too short"""
        deal_data = {
            "title": "Bad",  # Too short (min 5 chars)
            "description": "Valid description that is long enough for requirements.",
            "original_price": 100.0,
            "discounted_price": 50.0,
            "category": "food",
            "business_name": "Test Business",
            "location": {"city": "Warsaw"},
            "end_date": (datetime.utcnow() + timedelta(days=10)).isoformat()
        }

        response = await async_client.post(
            "/api/v1/deals/",
            json=deal_data,
            headers=auth_headers
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_deal_invalid_description_too_short(self, async_client, auth_headers):
        """Test validation: description too short"""
        deal_data = {
            "title": "Valid Title Here",
            "description": "Too short",  # Min 20 chars
            "original_price": 100.0,
            "discounted_price": 50.0,
            "category": "food",
            "business_name": "Test Business",
            "location": {"city": "Warsaw"},
            "end_date": (datetime.utcnow() + timedelta(days=10)).isoformat()
        }

        response = await async_client.post(
            "/api/v1/deals/",
            json=deal_data,
            headers=auth_headers
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_deal_invalid_prices(self, async_client, auth_headers):
        """Test validation: discounted price >= original price"""
        deal_data = {
            "title": "Invalid Price Deal",
            "description": "This deal has invalid pricing where discount is higher than original.",
            "original_price": 50.0,
            "discounted_price": 100.0,  # Higher than original!
            "category": "food",
            "business_name": "Test Business",
            "location": {"city": "Warsaw"},
            "end_date": (datetime.utcnow() + timedelta(days=10)).isoformat()
        }

        response = await async_client.post(
            "/api/v1/deals/",
            json=deal_data,
            headers=auth_headers
        )

        # Should either return 422 (validation) or calculate negative discount
        assert response.status_code in [422, 500]

    @pytest.mark.asyncio
    async def test_create_deal_missing_required_fields(self, async_client, auth_headers):
        """Test validation: missing required fields"""
        deal_data = {
            "title": "Incomplete Deal",
            # Missing description, prices, category, etc.
        }

        response = await async_client.post(
            "/api/v1/deals/",
            json=deal_data,
            headers=auth_headers
        )

        assert response.status_code == 422


# ============================================================================
# TEST: LIST DEALS (GET /api/v1/deals/)
# ============================================================================

class TestListDeals:
    """Test suite for listing deals"""

    @pytest.mark.asyncio
    async def test_list_deals_success(self, async_client, sample_deal):
        """Test successful deal listing"""
        response = await async_client.get("/api/v1/deals/")

        assert response.status_code == 200
        data = response.json()
        assert "deals" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert isinstance(data["deals"], list)

    @pytest.mark.asyncio
    async def test_list_deals_pagination(self, async_client, sample_deal):
        """Test pagination"""
        response = await async_client.get(
            "/api/v1/deals/",
            params={"page": 1, "page_size": 5}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 5
        assert len(data["deals"]) <= 5

    @pytest.mark.asyncio
    async def test_list_deals_filter_by_category(self, async_client, sample_deal):
        """Test filtering by category"""
        response = await async_client.get(
            "/api/v1/deals/",
            params={"category": "food"}
        )

        assert response.status_code == 200
        data = response.json()
        for deal in data["deals"]:
            assert deal["category"] == "food"

    @pytest.mark.asyncio
    async def test_list_deals_filter_by_city(self, async_client, sample_deal):
        """Test filtering by city"""
        response = await async_client.get(
            "/api/v1/deals/",
            params={"city": "Warsaw"}
        )

        assert response.status_code == 200
        data = response.json()
        # Deals should have Warsaw in location

    @pytest.mark.asyncio
    async def test_list_deals_search(self, async_client, sample_deal):
        """Test text search functionality"""
        response = await async_client.get(
            "/api/v1/deals/",
            params={"search": "Test"}
        )

        assert response.status_code == 200
        data = response.json()
        # Should find deals with "Test" in title/description

    @pytest.mark.asyncio
    async def test_list_deals_sorting(self, async_client, sample_deal):
        """Test sorting"""
        response = await async_client.get(
            "/api/v1/deals/",
            params={"sort_by": "discount_percentage", "sort_order": "desc"}
        )

        assert response.status_code == 200
        data = response.json()
        # Deals should be sorted by discount descending


# ============================================================================
# TEST: GET SINGLE DEAL (GET /api/v1/deals/{id})
# ============================================================================

class TestGetDeal:
    """Test suite for getting single deal"""

    @pytest.mark.asyncio
    async def test_get_deal_success(self, async_client, sample_deal):
        """Test successful deal retrieval"""
        deal_id = str(sample_deal.id)
        
        response = await async_client.get(f"/api/v1/deals/{deal_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == deal_id
        assert data["title"] == sample_deal.title

    @pytest.mark.asyncio
    async def test_get_deal_increments_views(self, async_client, sample_deal):
        """Test that getting a deal increments view count"""
        deal_id = str(sample_deal.id)
        initial_views = sample_deal.views_count

        response = await async_client.get(f"/api/v1/deals/{deal_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["views_count"] == initial_views + 1

    @pytest.mark.asyncio
    async def test_get_deal_not_found(self, async_client):
        """Test 404 for non-existent deal"""
        fake_id = str(PydanticObjectId())
        
        response = await async_client.get(f"/api/v1/deals/{fake_id}")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_deal_invalid_id(self, async_client):
        """Test invalid deal ID format"""
        response = await async_client.get("/api/v1/deals/invalid-id-format")

        assert response.status_code in [400, 422, 500]


# ============================================================================
# TEST: UPDATE DEAL (PUT /api/v1/deals/{id})
# ============================================================================

class TestUpdateDeal:
    """Test suite for updating deals"""

    @pytest.mark.asyncio
    async def test_update_deal_success(self, async_client, sample_deal, auth_headers):
        """Test successful deal update by owner"""
        deal_id = str(sample_deal.id)
        update_data = {
            "title": "Updated Test Deal",
            "discounted_price": 40.0  # Changed price
        }

        response = await async_client.put(
            f"/api/v1/deals/{deal_id}",
            json=update_data,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Test Deal"
        assert data["discounted_price"] == 40.0
        # Should recalculate discount
        assert data["discount_percentage"] == 60  # (100-40)/100 * 100

    @pytest.mark.asyncio
    async def test_update_deal_without_auth(self, async_client, sample_deal):
        """Test that updating without auth fails"""
        deal_id = str(sample_deal.id)
        update_data = {"title": "Should Fail"}

        response = await async_client.put(
            f"/api/v1/deals/{deal_id}",
            json=update_data
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_update_deal_wrong_owner(self, async_client, sample_deal):
        """Test that non-owner cannot update deal"""
        from app.core.security import create_access_token
        
        # Create token for different user
        wrong_token = create_access_token(data={"sub": "different_user_id"})
        wrong_headers = {"Authorization": f"Bearer {wrong_token}"}
        
        deal_id = str(sample_deal.id)
        update_data = {"title": "Should Fail"}

        response = await async_client.put(
            f"/api/v1/deals/{deal_id}",
            json=update_data,
            headers=wrong_headers
        )

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_update_deal_not_found(self, async_client, auth_headers):
        """Test 404 for updating non-existent deal"""
        fake_id = str(PydanticObjectId())
        update_data = {"title": "Won't Work"}

        response = await async_client.put(
            f"/api/v1/deals/{fake_id}",
            json=update_data,
            headers=auth_headers
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_deal_invalid_data(self, async_client, sample_deal, auth_headers):
        """Test validation on update"""
        deal_id = str(sample_deal.id)
        update_data = {
            "title": "Bad",  # Too short
            "discounted_price": -10  # Negative price
        }

        response = await async_client.put(
            f"/api/v1/deals/{deal_id}",
            json=update_data,
            headers=auth_headers
        )

        assert response.status_code == 422


# ============================================================================
# TEST: DELETE DEAL (DELETE /api/v1/deals/{id})
# ============================================================================

class TestDeleteDeal:
    """Test suite for deleting deals"""

    @pytest.mark.asyncio
    async def test_delete_deal_success(self, async_client, sample_deal, auth_headers):
        """Test successful deal deletion by owner"""
        deal_id = str(sample_deal.id)

        response = await async_client.delete(
            f"/api/v1/deals/{deal_id}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["deal_id"] == deal_id

        # Verify deal is actually deleted
        get_response = await async_client.get(f"/api/v1/deals/{deal_id}")
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_deal_without_auth(self, async_client, sample_deal):
        """Test that deleting without auth fails"""
        deal_id = str(sample_deal.id)

        response = await async_client.delete(f"/api/v1/deals/{deal_id}")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_delete_deal_wrong_owner(self, async_client, sample_deal):
        """Test that non-owner cannot delete deal"""
        from app.core.security import create_access_token
        
        wrong_token = create_access_token(data={"sub": "different_user_id"})
        wrong_headers = {"Authorization": f"Bearer {wrong_token}"}
        
        deal_id = str(sample_deal.id)

        response = await async_client.delete(
            f"/api/v1/deals/{deal_id}",
            headers=wrong_headers
        )

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_delete_deal_not_found(self, async_client, auth_headers):
        """Test 404 for deleting non-existent deal"""
        fake_id = str(PydanticObjectId())

        response = await async_client.delete(
            f"/api/v1/deals/{fake_id}",
            headers=auth_headers
        )

        assert response.status_code == 404


# ============================================================================
# TEST: BONUS ENDPOINTS
# ============================================================================

class TestBonusEndpoints:
    """Test suite for bonus endpoints"""

    @pytest.mark.asyncio
    async def test_get_deals_by_category(self, async_client, sample_deal):
        """Test GET /api/v1/deals/category/{category}"""
        response = await async_client.get("/api/v1/deals/category/food")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        for deal in data:
            assert deal["category"] == "food"

    @pytest.mark.asyncio
    async def test_get_my_deals(self, async_client, sample_deal, auth_headers):
        """Test GET /api/v1/deals/user/my-deals"""
        response = await async_client.get(
            "/api/v1/deals/user/my-deals",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Should return deals created by authenticated user

    @pytest.mark.asyncio
    async def test_get_my_deals_without_auth(self, async_client):
        """Test that my-deals requires auth"""
        response = await async_client.get("/api/v1/deals/user/my-deals")

        assert response.status_code == 401


# ============================================================================
# TEST: ERROR HANDLING
# ============================================================================

class TestErrorHandling:
    """Test suite for error handling"""

    @pytest.mark.asyncio
    async def test_invalid_json_body(self, async_client, auth_headers):
        """Test handling of invalid JSON"""
        response = await async_client.post(
            "/api/v1/deals/",
            content="invalid json{{{",
            headers={**auth_headers, "Content-Type": "application/json"}
        )

        assert response.status_code in [400, 422]

    @pytest.mark.asyncio
    async def test_invalid_query_params(self, async_client):
        """Test handling of invalid query parameters"""
        response = await async_client.get(
            "/api/v1/deals/",
            params={"page": -1, "page_size": 1000}  # Invalid values
        )

        # Should either reject or use defaults
        assert response.status_code in [200, 422]


# ============================================================================
# TEST: INTEGRATION SCENARIOS
# ============================================================================

class TestIntegrationScenarios:
    """Integration tests for complete workflows"""

    @pytest.mark.asyncio
    async def test_full_deal_lifecycle(self, async_client, auth_headers):
        """Test complete deal lifecycle: create → read → update → delete"""
        
        # 1. Create deal
        deal_data = {
            "title": "Lifecycle Test Deal",
            "description": "Testing the complete lifecycle of a deal from creation to deletion.",
            "original_price": 200.0,
            "discounted_price": 100.0,
            "category": "shopping",
            "business_name": "Lifecycle Test Business",
            "location": {"city": "Warsaw"},
            "end_date": (datetime.utcnow() + timedelta(days=7)).isoformat()
        }
        
        create_response = await async_client.post(
            "/api/v1/deals/",
            json=deal_data,
            headers=auth_headers
        )
        assert create_response.status_code == 201
        deal_id = create_response.json()["id"]
        
        # 2. Read deal
        get_response = await async_client.get(f"/api/v1/deals/{deal_id}")
        assert get_response.status_code == 200
        assert get_response.json()["title"] == "Lifecycle Test Deal"
        
        # 3. Update deal
        update_response = await async_client.put(
            f"/api/v1/deals/{deal_id}",
            json={"title": "Updated Lifecycle Deal"},
            headers=auth_headers
        )
        assert update_response.status_code == 200
        assert update_response.json()["title"] == "Updated Lifecycle Deal"
        
        # 4. Delete deal
        delete_response = await async_client.delete(
            f"/api/v1/deals/{deal_id}",
            headers=auth_headers
        )
        assert delete_response.status_code == 200
        
        # 5. Verify deletion
        final_get = await async_client.get(f"/api/v1/deals/{deal_id}")
        assert final_get.status_code == 404

    @pytest.mark.asyncio
    async def test_concurrent_view_increments(self, async_client, sample_deal):
        """Test concurrent view count increments"""
        deal_id = str(sample_deal.id)
        initial_views = sample_deal.views_count
        
        # Simulate multiple concurrent views
        import asyncio
        tasks = [
            async_client.get(f"/api/v1/deals/{deal_id}")
            for _ in range(5)
        ]
        responses = await asyncio.gather(*tasks)
        
        # All should succeed
        assert all(r.status_code == 200 for r in responses)
        
        # Final view count should be initial + 5
        final_response = await async_client.get(f"/api/v1/deals/{deal_id}")
        final_views = final_response.json()["views_count"]
        assert final_views >= initial_views + 5


# ============================================================================
# TEST: BUSINESS LOGIC
# ============================================================================

class TestBusinessLogic:
    """Test business logic and calculations"""

    @pytest.mark.asyncio
    async def test_discount_percentage_calculation(self, async_client, auth_headers):
        """Test automatic discount percentage calculation"""
        deal_data = {
            "title": "Discount Calculation Test",
            "description": "Testing automatic calculation of discount percentage based on prices.",
            "original_price": 100.0,
            "discounted_price": 25.0,  # Should be 75% discount
            "category": "food",
            "business_name": "Test Business",
            "location": {"city": "Warsaw"},
            "end_date": (datetime.utcnow() + timedelta(days=5)).isoformat()
        }

        response = await async_client.post(
            "/api/v1/deals/",
            json=deal_data,
            headers=auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["discount_percentage"] == 75

    @pytest.mark.asyncio
    async def test_deal_expiration_check(self, async_client, auth_headers):
        """Test deal expiration logic"""
        # Create expired deal
        deal_data = {
            "title": "Expired Deal",
            "description": "This deal has already expired and should not appear in active listings.",
            "original_price": 100.0,
            "discounted_price": 50.0,
            "category": "food",
            "business_name": "Test Business",
            "location": {"city": "Warsaw"},
            "start_date": (datetime.utcnow() - timedelta(days=10)).isoformat(),
            "end_date": (datetime.utcnow() - timedelta(days=1)).isoformat()  # Yesterday
        }

        create_response = await async_client.post(
            "/api/v1/deals/",
            json=deal_data,
            headers=auth_headers
        )
        
        # Deal should be created but marked as expired or not shown in active list
        # This depends on your business logic


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=app.api.routes.deals", "--cov-report=html"])
