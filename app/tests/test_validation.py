"""
Validation Tests for SaveMate Deals API
Tests data validation and business logic without requiring database
"""

import pytest
from datetime import datetime, timedelta
from pydantic import ValidationError


class TestDealValidation:
    """Test deal data validation using Pydantic schemas"""
    
    def test_title_min_length(self):
        """Test title minimum length validation (min 5 chars)"""
        from app.schemas.deal_schema import DealCreate
        
        # Title too short (< 5 chars)
        with pytest.raises(ValidationError) as exc_info:
            DealCreate(
                title="Bad",  # Only 3 chars - should fail
                description="A valid description with sufficient length for all requirements and validation.",
                original_price=100.0,
                discounted_price=50.0,
                category="food",
                business_name="Test Business",
                location={
                    "address": "Test Street 123",
                    "city": "Warsaw",
                    "postal_code": "00-001",
                    "country": "Poland"
                },
                end_date=datetime.utcnow() + timedelta(days=7)
            )
        
        assert "title" in str(exc_info.value).lower()
        print("✅ Title min length validation works (requires 5+ chars)")
    
    def test_title_max_length(self):
        """Test title maximum length validation (max 200 chars)"""
        from app.schemas.deal_schema import DealCreate
        
        # Title too long (> 200 chars)
        with pytest.raises(ValidationError) as exc_info:
            DealCreate(
                title="X" * 201,  # 201 chars - should fail
                description="A valid description with sufficient length for all requirements and validation.",
                original_price=100.0,
                discounted_price=50.0,
                category="food",
                business_name="Test Business",
                location={
                    "address": "Test Street 123",
                    "city": "Warsaw",
                    "postal_code": "00-001",
                    "country": "Poland"
                },
                end_date=datetime.utcnow() + timedelta(days=7)
            )
        
        assert "title" in str(exc_info.value).lower()
        print("✅ Title max length validation works (max 200 chars)")
    
    def test_description_min_length(self):
        """Test description minimum length validation (min 20 chars)"""
        from app.schemas.deal_schema import DealCreate
        
        # Description too short (< 20 chars)
        with pytest.raises(ValidationError) as exc_info:
            DealCreate(
                title="Valid Deal Title",
                description="Too short",  # Only 9 chars - should fail
                original_price=100.0,
                discounted_price=50.0,
                category="food",
                business_name="Test Business",
                location={
                    "address": "Test Street 123",
                    "city": "Warsaw",
                    "postal_code": "00-001",
                    "country": "Poland"
                },
                end_date=datetime.utcnow() + timedelta(days=7)
            )
        
        assert "description" in str(exc_info.value).lower()
        print("✅ Description min length validation works (requires 20+ chars)")
    
    def test_description_max_length(self):
        """Test description maximum length validation (max 2000 chars)"""
        from app.schemas.deal_schema import DealCreate
        
        # Description too long (> 2000 chars)
        with pytest.raises(ValidationError) as exc_info:
            DealCreate(
                title="Valid Deal Title",
                description="X" * 2001,  # 2001 chars - should fail
                original_price=100.0,
                discounted_price=50.0,
                category="food",
                business_name="Test Business",
                location={
                    "address": "Test Street 123",
                    "city": "Warsaw",
                    "postal_code": "00-001",
                    "country": "Poland"
                },
                end_date=datetime.utcnow() + timedelta(days=7)
            )
        
        assert "description" in str(exc_info.value).lower()
        print("✅ Description max length validation works (max 2000 chars)")
    
    def test_original_price_must_be_positive(self):
        """Test that original price must be positive (> 0)"""
        from app.schemas.deal_schema import DealCreate
        
        # Negative original price
        with pytest.raises(ValidationError) as exc_info:
            DealCreate(
                title="Valid Deal Title",
                description="A valid description with sufficient length for all requirements and validation.",
                original_price=-100.0,  # Negative - should fail
                discounted_price=50.0,
                category="food",
                business_name="Test Business",
                location={
                    "address": "Test Street 123",
                    "city": "Warsaw",
                    "postal_code": "00-001",
                    "country": "Poland"
                },
                end_date=datetime.utcnow() + timedelta(days=7)
            )
        
        assert "original_price" in str(exc_info.value).lower()
        print("✅ Original price must be positive validation works")
    
    def test_discounted_price_must_be_positive(self):
        """Test that discounted price must be positive (> 0)"""
        from app.schemas.deal_schema import DealCreate
        
        # Negative discounted price
        with pytest.raises(ValidationError) as exc_info:
            DealCreate(
                title="Valid Deal Title",
                description="A valid description with sufficient length for all requirements and validation.",
                original_price=100.0,
                discounted_price=-50.0,  # Negative - should fail
                category="food",
                business_name="Test Business",
                location={
                    "address": "Test Street 123",
                    "city": "Warsaw",
                    "postal_code": "00-001",
                    "country": "Poland"
                },
                end_date=datetime.utcnow() + timedelta(days=7)
            )
        
        assert "discounted_price" in str(exc_info.value).lower()
        print("✅ Discounted price must be positive validation works")
    
    def test_zero_price_not_allowed(self):
        """Test that zero prices are not allowed"""
        from app.schemas.deal_schema import DealCreate
        
        # Zero price
        with pytest.raises(ValidationError) as exc_info:
            DealCreate(
                title="Valid Deal Title",
                description="A valid description with sufficient length for all requirements and validation.",
                original_price=0.0,  # Zero - should fail
                discounted_price=50.0,
                category="food",
                business_name="Test Business",
                location={
                    "address": "Test Street 123",
                    "city": "Warsaw",
                    "postal_code": "00-001",
                    "country": "Poland"
                },
                end_date=datetime.utcnow() + timedelta(days=7)
            )
        
        assert "original_price" in str(exc_info.value).lower()
        print("✅ Zero price validation works")
    
    def test_category_must_be_valid_enum(self):
        """Test category must be from valid enum values"""
        from app.schemas.deal_schema import DealCreate
        
        # Invalid category (not in enum)
        with pytest.raises(ValidationError) as exc_info:
            DealCreate(
                title="Valid Deal Title",
                description="A valid description with sufficient length for all requirements and validation.",
                original_price=100.0,
                discounted_price=50.0,
                category="invalid_category_xyz",  # Invalid - should fail
                business_name="Test Business",
                location={
                    "address": "Test Street 123",
                    "city": "Warsaw",
                    "postal_code": "00-001",
                    "country": "Poland"
                },
                end_date=datetime.utcnow() + timedelta(days=7)
            )
        
        assert "category" in str(exc_info.value).lower()
        print("✅ Category enum validation works")
    
    def test_valid_deal_creation(self):
        """Test that valid deal with all correct fields passes validation"""
        from app.schemas.deal_schema import DealCreate
        
        # Create valid deal with all required fields
        deal = DealCreate(
            title="Valid Deal Title Here",
            description="This is a valid and comprehensive description with sufficient length to meet all validation requirements.",
            original_price=100.0,
            discounted_price=50.0,
            category="food",
            business_name="Test Business Name",
            location={
                "address": "Test Street 123",
                "city": "Warsaw",
                "postal_code": "00-001",
                "country": "Poland"
            },
            end_date=datetime.utcnow() + timedelta(days=7)
        )
        
        # Verify fields
        assert deal.title == "Valid Deal Title Here"
        assert deal.original_price == 100.0
        assert deal.discounted_price == 50.0
        assert deal.category == "food"
        assert deal.location["city"] == "Warsaw"
        
        print("✅ Valid deal creation works with all required fields")
    
    def test_all_valid_categories(self):
        """Test that all valid category enums are accepted"""
        from app.schemas.deal_schema import DealCreate
        from app.models.deal import DealCategory
        
        valid_categories = [
            "food", "drinks", "shopping", "entertainment",
            "health", "beauty", "services", "travel",
            "electronics", "other"
        ]
        
        for category in valid_categories:
            deal = DealCreate(
                title="Valid Deal Title",
                description="A valid description with sufficient length for all requirements and validation.",
                original_price=100.0,
                discounted_price=50.0,
                category=category,
                business_name="Test Business",
                location={
                    "address": "Test Street 123",
                    "city": "Warsaw",
                    "postal_code": "00-001",
                    "country": "Poland"
                },
                end_date=datetime.utcnow() + timedelta(days=7)
            )
            assert deal.category == category
        
        print(f"✅ All {len(valid_categories)} valid categories accepted")


class TestDealModelLogic:
    """Test Deal model business logic methods"""
    
    def test_discount_calculation_50_percent(self):
        """Test discount percentage calculation - 50% discount"""
        from app.models.deal import Deal
        
        deal = Deal(
            title="Test Deal Title",
            description="Test description with sufficient length for all requirements and validation purposes.",
            original_price=100.0,
            discounted_price=50.0,
            category="food",
            business_id="674890abcdef123456789012",
            business_name="Test Business",
            location={
                "address": "Test Street 123",
                "city": "Warsaw",
                "postal_code": "00-001",
                "country": "Poland"
            },
            end_date=datetime.utcnow() + timedelta(days=7),
            created_by="674890abcdef123456789012"
        )
        
        # Calculate discount
        deal.calculate_discount_percentage()
        
        assert deal.discount_percentage == 50
        print("✅ Discount calculation works: 50% off (100 → 50)")
    
    def test_discount_calculation_75_percent(self):
        """Test discount percentage calculation - 75% discount"""
        from app.models.deal import Deal
        
        deal = Deal(
            title="Test Deal Title",
            description="Test description with sufficient length for all requirements and validation purposes.",
            original_price=100.0,
            discounted_price=25.0,
            category="food",
            business_id="674890abcdef123456789012",
            business_name="Test Business",
            location={
                "address": "Test Street 123",
                "city": "Warsaw",
                "postal_code": "00-001",
                "country": "Poland"
            },
            end_date=datetime.utcnow() + timedelta(days=7),
            created_by="674890abcdef123456789012"
        )
        
        # Calculate discount
        deal.calculate_discount_percentage()
        
        assert deal.discount_percentage == 75
        print("✅ Discount calculation works: 75% off (100 → 25)")
    
    def test_discount_calculation_25_percent(self):
        """Test discount percentage calculation - 25% discount"""
        from app.models.deal import Deal
        
        deal = Deal(
            title="Test Deal Title",
            description="Test description with sufficient length for all requirements and validation purposes.",
            original_price=200.0,
            discounted_price=150.0,
            category="food",
            business_id="674890abcdef123456789012",
            business_name="Test Business",
            location={
                "address": "Test Street 123",
                "city": "Warsaw",
                "postal_code": "00-001",
                "country": "Poland"
            },
            end_date=datetime.utcnow() + timedelta(days=7),
            created_by="674890abcdef123456789012"
        )
        
        # Calculate discount
        deal.calculate_discount_percentage()
        
        assert deal.discount_percentage == 25
        print("✅ Discount calculation works: 25% off (200 → 150)")
    
    def test_is_expired_returns_false_for_future_date(self):
        """Test deal is NOT expired when end_date is in the future"""
        from app.models.deal import Deal
        
        deal = Deal(
            title="Test Deal Title",
            description="Test description with sufficient length for all requirements and validation purposes.",
            original_price=100.0,
            discounted_price=50.0,
            category="food",
            business_id="674890abcdef123456789012",
            business_name="Test Business",
            location={
                "address": "Test Street 123",
                "city": "Warsaw",
                "postal_code": "00-001",
                "country": "Poland"
            },
            end_date=datetime.utcnow() + timedelta(days=7),  # 7 days in future
            created_by="674890abcdef123456789012"
        )
        
        # Check expiration
        is_expired = deal.is_expired()
        
        assert is_expired == False
        print("✅ is_expired() correctly returns False for future dates")
    
    def test_is_expired_returns_true_for_past_date(self):
        """Test deal IS expired when end_date is in the past"""
        from app.models.deal import Deal
        
        deal = Deal(
            title="Test Deal Title",
            description="Test description with sufficient length for all requirements and validation purposes.",
            original_price=100.0,
            discounted_price=50.0,
            category="food",
            business_id="674890abcdef123456789012",
            business_name="Test Business",
            location={
                "address": "Test Street 123",
                "city": "Warsaw",
                "postal_code": "00-001",
                "country": "Poland"
            },
            end_date=datetime.utcnow() - timedelta(days=1),  # Yesterday
            created_by="674890abcdef123456789012"
        )
        
        # Check expiration
        is_expired = deal.is_expired()
        
        assert is_expired == True
        print("✅ is_expired() correctly returns True for past dates")
    
    def test_is_valid_returns_true_for_active_valid_deal(self):
        """Test deal is valid when active and within date range"""
        from app.models.deal import Deal, DealStatus
        
        deal = Deal(
            title="Test Deal Title",
            description="Test description with sufficient length for all requirements and validation purposes.",
            original_price=100.0,
            discounted_price=50.0,
            category="food",
            business_id="674890abcdef123456789012",
            business_name="Test Business",
            location={
                "address": "Test Street 123",
                "city": "Warsaw",
                "postal_code": "00-001",
                "country": "Poland"
            },
            start_date=datetime.utcnow() - timedelta(days=1),  # Started yesterday
            end_date=datetime.utcnow() + timedelta(days=7),  # Ends in 7 days
            status=DealStatus.ACTIVE,
            created_by="674890abcdef123456789012"
        )
        
        # Check validity
        is_valid = deal.is_valid()
        
        assert is_valid == True
        print("✅ is_valid() correctly returns True for active, current deals")
    
    def test_is_valid_returns_false_for_inactive_deal(self):
        """Test deal is invalid when status is not active"""
        from app.models.deal import Deal, DealStatus
        
        deal = Deal(
            title="Test Deal Title",
            description="Test description with sufficient length for all requirements and validation purposes.",
            original_price=100.0,
            discounted_price=50.0,
            category="food",
            business_id="674890abcdef123456789012",
            business_name="Test Business",
            location={
                "address": "Test Street 123",
                "city": "Warsaw",
                "postal_code": "00-001",
                "country": "Poland"
            },
            start_date=datetime.utcnow() - timedelta(days=1),
            end_date=datetime.utcnow() + timedelta(days=7),
            status=DealStatus.INACTIVE,  # Inactive status
            created_by="674890abcdef123456789012"
        )
        
        # Check validity
        is_valid = deal.is_valid()
        
        assert is_valid == False
        print("✅ is_valid() correctly returns False for inactive deals")


# Run tests with coverage if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "--cov=app.models.deal", "--cov=app.schemas.deal_schema"])