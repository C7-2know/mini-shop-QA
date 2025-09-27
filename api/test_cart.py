"""
Cart API tests for MiniShop.
"""
import pytest
# import jsonschema
from common.api_client import MiniShopAPI
from common.test_data import TestData, TestDataBuilder


@pytest.mark.api
@pytest.mark.functional
class TestCart:
    """Test cart endpoints."""
    
    @pytest.fixture(autouse=True)
    def setup(self, config):
        """Setup test fixtures."""
        self.api = MiniShopAPI(config.API_BASE_URL)
        self.data_builder = TestDataBuilder()
    
    def test_add_single_item_to_cart(self):
        """Test adding a single item to cart."""
        # Arrange
        items = self.data_builder.single_cart_item(product_id=1, quantity=2)
        
        # Act
        response = self.api.add_to_cart(items)
        
        # Assert
        assert "cartId" in response
        assert "totalBeforeTax" in response
        assert response["totalBeforeTax"] == 40.0  # 2 * 20.0 (Shirt price)
        
        # Validate response schema
        # jsonschema.validate(response, TestData.CART_RESPONSE_SCHEMA)
    
    def test_add_multiple_items_to_cart(self):
        """Test adding multiple different items to cart."""
        # Arrange
        items = [
            {"productId": 1, "qty": 2},  # Shirt: 2 * 20 = 40
            {"productId": 2, "qty": 1},  # Hat: 1 * 15 = 15
            {"productId": 3, "qty": 1}   # Skirt: 1 * 30 = 30
        ]
        
        # Act
        response = self.api.add_to_cart(items)
        
        # Assert
        assert response["totalBeforeTax"] == 85.0  # 40 + 15 + 30
        assert "cart" in response["cartId"]
    
    def test_add_duplicate_items_consolidates_quantity(self):
        """Test that adding duplicate items consolidates quantity."""
        # Arrange
        items = self.data_builder.duplicate_cart_items(product_id=1)
        # Two separate entries for same product: qty 2 and qty 3
        
        # Act
        response = self.api.add_to_cart(items)
        
        # Assert
        # Should consolidate to qty 5: 5 * 20 = 100
        assert response["totalBeforeTax"] == 100.0
        assert "cart-1x2-1x3" in response["cartId"]  # Cart ID shows both entries
    
    def test_add_nonexistent_product_returns_400(self):
        """Test adding non-existent product returns 400 error."""
        # Arrange
        items = self.data_builder.invalid_cart_items()
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            self.api.add_to_cart(items)
        
        assert "400" in str(exc_info.value) or "Product not found" in str(exc_info.value)
    
    def test_add_zero_quantity_item(self):
        """Test adding item with zero quantity."""
        # Arrange
        items = [{"productId": 1, "qty": 0}]
        
        # Act
        response = self.api.add_to_cart(items)
        
        # Assert
        assert response["totalBeforeTax"] == 0.0
    