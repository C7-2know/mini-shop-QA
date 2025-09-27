"""
Products API tests for MiniShop.
"""
import pytest
from common.api_client import MiniShopAPI
from common.test_data import TestData, TestDataBuilder


@pytest.mark.api
@pytest.mark.functional
class TestProducts:
    """Test products endpoints."""
    
    @pytest.fixture(autouse=True)
    def setup(self, config):
        """Setup test fixtures."""
        self.api = MiniShopAPI(config.API_BASE_URL)
        self.data_builder = TestDataBuilder()
    
    def test_get_all_products(self):
        """Test getting all products without filters."""
        # Act
        products = self.api.get_products()
        
        # Assert
        assert len(products) == 8  # Expected number of products
        assert all("id" in p and "name" in p and "price" in p and "category" in p for p in products)
        
    
    def test_get_products_by_category(self):
        """Test filtering products by category."""
        # Act
        clothing_products = self.api.get_products(category="Clothing")
        
        # Assert
        assert len(clothing_products) > 0
        assert all(p["category"] == "Clothing" for p in clothing_products)
        
        # Test different categories
        electronics = self.api.get_products(category="Electronics")
        assert len(electronics) > 0
        assert all(p["category"] == "Electronics" for p in electronics)
    
    def test_get_products_by_price_range(self):
        """Test filtering products by price range."""
        # Act
        cheap_products = self.api.get_products(min_price=0, max_price=20)
        
        # Assert
        assert len(cheap_products) > 0
        assert all(0 <= p["price"] <= 20 for p in cheap_products)
    
    def test_get_products_combined_filters(self):
        """Test filtering products with multiple criteria."""
        # Act
        filtered_products = self.api.get_products(
            category="Clothing",
            min_price=10,
            max_price=50
        )
        
        # Assert
        assert len(filtered_products) > 0
        assert all(
            p["category"] == "Clothing" and 10 <= p["price"] <= 50 
            for p in filtered_products
        )
    
    def test_get_products_boundary_prices(self):
        """Test boundary price filtering."""
        # Test exact price match
        exact_price = self.api.get_products(min_price=20, max_price=20)
        assert len(exact_price) > 0
        assert all(p["price"] == 20 for p in exact_price)
        
        # Test no products in range
        no_products = self.api.get_products(min_price=1000, max_price=2000)
        assert len(no_products) == 0
    
    def test_get_products_negative_price_range(self):
        """Test negative price range handling."""
        # Act
        products = self.api.get_products(min_price=-10, max_price=10)
        
        # Assert - should handle negative prices gracefully
        assert isinstance(products, list)
    
    def test_get_products_large_price_range(self):
        """Test large price range."""
        # Act
        products = self.api.get_products(min_price=0, max_price=10000)
        
        # Assert
        assert len(products) == 8  # Should return all products
        assert all(0 <= p["price"] <= 10000 for p in products)
    
