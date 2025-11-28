"""
Category API Tests for SaveMate
Tests validation, API endpoints, and business logic
"""

import pytest
from datetime import datetime
from pydantic import ValidationError


class TestCategoryValidation:
    """Test category data validation using Pydantic schemas"""
    
    def test_valid_category_creation(self):
        """Test valid category passes all validation"""
        from app.schemas.category_schema import CategoryCreate
        
        category = CategoryCreate(
            name="Food & Dining",
            slug="food-dining",
            description="Restaurants, cafes, and food delivery services",
            icon="🍔",
            color="#EF4444",
            order=1,
            is_featured=True
        )
        
        assert category.name == "Food & Dining"
        assert category.slug == "food-dining"
        assert category.icon == "🍔"
        assert category.color == "#EF4444"
        print("✅ Valid category creation works")
    
    def test_name_min_length(self):
        """Test category name minimum length (2 chars)"""
        from app.schemas.category_schema import CategoryCreate
        
        with pytest.raises(ValidationError) as exc_info:
            CategoryCreate(
                name="F",  # Too short
                slug="food",
                description="Test category"
            )
        
        assert "name" in str(exc_info.value).lower()
        print("✅ Name min length validation works")
    
    def test_name_max_length(self):
        """Test category name maximum length (100 chars)"""
        from app.schemas.category_schema import CategoryCreate
        
        with pytest.raises(ValidationError) as exc_info:
            CategoryCreate(
                name="X" * 101,  # Too long
                slug="test",
                description="Test category"
            )
        
        assert "name" in str(exc_info.value).lower()
        print("✅ Name max length validation works")
    
    def test_slug_format_validation(self):
        """Test slug must be URL-friendly (lowercase, numbers, hyphens only)"""
        from app.schemas.category_schema import CategoryCreate
        
        # Invalid slug with uppercase
        with pytest.raises(ValidationError):
            CategoryCreate(
                name="Food",
                slug="Food-Dining",  # Uppercase not allowed
                description="Test"
            )
        
        # Invalid slug with spaces
        with pytest.raises(ValidationError):
            CategoryCreate(
                name="Food",
                slug="food dining",  # Spaces not allowed
                description="Test"
            )
        
        # Invalid slug with special chars
        with pytest.raises(ValidationError):
            CategoryCreate(
                name="Food",
                slug="food@dining",  # Special chars not allowed
                description="Test"
            )
        
        # Valid slug
        category = CategoryCreate(
            name="Food",
            slug="food-dining-123",  # Valid: lowercase, numbers, hyphens
            description="Test"
        )
        assert category.slug == "food-dining-123"
        
        print("✅ Slug format validation works")
    
    def test_color_hex_validation(self):
        """Test color must be valid hex code (#RRGGBB)"""
        from app.schemas.category_schema import CategoryCreate
        
        # Invalid: no hash
        with pytest.raises(ValidationError):
            CategoryCreate(
                name="Food",
                slug="food",
                color="FF0000"  # Missing #
            )
        
        # Invalid: wrong length
        with pytest.raises(ValidationError):
            CategoryCreate(
                name="Food",
                slug="food",
                color="#FF00"  # Too short
            )
        
        # Invalid: invalid characters
        with pytest.raises(ValidationError):
            CategoryCreate(
                name="Food",
                slug="food",
                color="#GGGGGG"  # G is not hex
            )
        
        # Valid colors
        valid_colors = ["#FF0000", "#3B82F6", "#10b981", "#FFFFFF"]
        for color in valid_colors:
            category = CategoryCreate(
                name="Food",
                slug="food",
                color=color
            )
            assert category.color == color
        
        print("✅ Color hex validation works")
    
    def test_description_max_length(self):
        """Test description maximum length (500 chars)"""
        from app.schemas.category_schema import CategoryCreate
        
        with pytest.raises(ValidationError):
            CategoryCreate(
                name="Food",
                slug="food",
                description="X" * 501  # Too long
            )
        
        # Valid at exactly 500 chars
        category = CategoryCreate(
            name="Food",
            slug="food",
            description="X" * 500
        )
        assert len(category.description) == 500
        
        print("✅ Description max length validation works")
    
    def test_order_must_be_non_negative(self):
        """Test order must be >= 0"""
        from app.schemas.category_schema import CategoryCreate
        
        with pytest.raises(ValidationError):
            CategoryCreate(
                name="Food",
                slug="food",
                order=-1  # Negative not allowed
            )
        
        # Valid at 0
        category = CategoryCreate(
            name="Food",
            slug="food",
            order=0
        )
        assert category.order == 0
        
        print("✅ Order non-negative validation works")
    
    def test_optional_fields_have_defaults(self):
        """Test optional fields have sensible defaults"""
        from app.schemas.category_schema import CategoryCreate
        
        # Minimal category
        category = CategoryCreate(
            name="Food",
            slug="food"
        )
        
        assert category.icon == "tag"  # Default icon
        assert category.color == "#3B82F6"  # Default color
        assert category.order == 0  # Default order
        assert category.is_active == True  # Default active
        assert category.is_featured == False  # Default not featured
        assert category.description is None  # Optional
        assert category.parent_category is None  # Optional
        
        print("✅ Optional fields have correct defaults")
    
    def test_partial_update_validation(self):
        """Test CategoryUpdate allows partial updates"""
        from app.schemas.category_schema import CategoryUpdate
        
        # Update only name
        update = CategoryUpdate(name="New Name")
        assert update.name == "New Name"
        assert update.slug is None
        
        # Update only color
        update = CategoryUpdate(color="#FF0000")
        assert update.color == "#FF0000"
        assert update.name is None
        
        # Update multiple fields
        update = CategoryUpdate(
            name="New Name",
            slug="new-slug",
            is_featured=True
        )
        assert update.name == "New Name"
        assert update.slug == "new-slug"
        assert update.is_featured == True
        
        print("✅ Partial update validation works")


class TestCategoryModelLogic:
    """Test Category model business logic"""
    
    def test_category_creation_with_all_fields(self):
        """Test creating category model with all fields"""
        from app.models.category import Category
        
        category = Category(
            name="Food & Dining",
            slug="food-dining",
            description="Restaurants and cafes",
            icon="🍔",
            color="#EF4444",
            image="https://example.com/food.jpg",
            parent_category=None,
            order=1,
            deals_count=0,
            is_active=True,
            is_featured=True,
            created_at=datetime.utcnow()
        )
        
        assert category.name == "Food & Dining"
        assert category.slug == "food-dining"
        assert category.deals_count == 0
        assert category.is_active == True
        assert category.is_featured == True
        
        print("✅ Category model creation works")
    
    def test_category_defaults(self):
        """Test category model default values"""
        from app.models.category import Category
        
        category = Category(
            name="Test",
            slug="test"
        )
        
        assert category.icon == "tag"
        assert category.color == "#3B82F6"
        assert category.order == 0
        assert category.deals_count == 0
        assert category.is_active == True
        assert category.is_featured == False
        
        print("✅ Category model defaults work")
    
    def test_hierarchical_categories(self):
        """Test parent-child category relationships"""
        from app.models.category import Category
        
        # Parent category
        parent = Category(
            name="Food",
            slug="food"
        )
        
        # Child category
        child = Category(
            name="Fast Food",
            slug="fast-food",
            parent_category="parent_id_here"
        )
        
        assert child.parent_category == "parent_id_here"
        assert parent.parent_category is None
        
        print("✅ Hierarchical categories work")


class TestCategorySchemas:
    """Test category schema transformations"""
    
    def test_category_response_schema(self):
        """Test CategoryResponse includes all fields"""
        from app.schemas.category_schema import CategoryResponse
        
        response = CategoryResponse(
            id="674890abcdef123456789012",
            name="Food",
            slug="food",
            description="Food category",
            icon="🍔",
            color="#EF4444",
            image=None,
            parent_category=None,
            order=1,
            deals_count=15,
            is_active=True,
            is_featured=True,
            created_at=datetime.utcnow()
        )
        
        assert response.id == "674890abcdef123456789012"
        assert response.deals_count == 15
        assert response.created_at is not None
        
        print("✅ CategoryResponse schema works")
    
    def test_category_summary_schema(self):
        """Test CategorySummary for simplified listings"""
        from app.schemas.category_schema import CategorySummary
        
        summary = CategorySummary(
            id="674890abcdef123456789012",
            name="Food",
            slug="food",
            icon="🍔",
            color="#EF4444",
            deals_count=15,
            is_featured=True
        )
        
        assert summary.id == "674890abcdef123456789012"
        assert summary.deals_count == 15
        
        print("✅ CategorySummary schema works")
    
    def test_category_list_response_schema(self):
        """Test CategoryListResponse with pagination"""
        from app.schemas.category_schema import CategoryListResponse, CategoryResponse
        
        response = CategoryListResponse(
            categories=[
                CategoryResponse(
                    id="1",
                    name="Food",
                    slug="food",
                    description=None,
                    icon="🍔",
                    color="#EF4444",
                    image=None,
                    parent_category=None,
                    order=1,
                    deals_count=15,
                    is_active=True,
                    is_featured=True,
                    created_at=datetime.utcnow()
                )
            ],
            total=10,
            page=1,
            page_size=10,
            total_pages=1
        )
        
        assert len(response.categories) == 1
        assert response.total == 10
        assert response.page == 1
        assert response.total_pages == 1
        
        print("✅ CategoryListResponse schema works")


class TestCategoryValidationEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_slug_edge_cases(self):
        """Test slug validation edge cases"""
        from app.schemas.category_schema import CategoryCreate
        
        # Valid edge cases
        valid_slugs = [
            "a",  # Single char
            "a-b",  # With hyphen
            "a-b-c-d",  # Multiple hyphens
            "test123",  # With numbers
            "123test",  # Starting with number
            "a" * 100,  # Maximum length
        ]
        
        for slug in valid_slugs:
            category = CategoryCreate(name="Test", slug=slug)
            assert category.slug == slug
        
        print("✅ Slug edge cases work")
    
    def test_color_case_insensitivity(self):
        """Test that hex colors accept both upper and lowercase"""
        from app.schemas.category_schema import CategoryCreate
        
        # Both should be valid
        cat1 = CategoryCreate(name="Test", slug="test", color="#FFFFFF")
        cat2 = CategoryCreate(name="Test2", slug="test2", color="#ffffff")
        cat3 = CategoryCreate(name="Test3", slug="test3", color="#AbCdEf")
        
        assert cat1.color == "#FFFFFF"
        assert cat2.color == "#ffffff"
        assert cat3.color == "#AbCdEf"
        
        print("✅ Color case handling works")
    
    def test_empty_optional_fields(self):
        """Test that optional fields can be None or empty"""
        from app.schemas.category_schema import CategoryCreate
        
        category = CategoryCreate(
            name="Test",
            slug="test",
            description=None,  # Explicitly None
            parent_category=None,
            image=None
        )
        
        assert category.description is None
        assert category.parent_category is None
        assert category.image is None
        
        print("✅ Empty optional fields work")


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
