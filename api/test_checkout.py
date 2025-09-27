"""
Checkout API tests for MiniShop.
"""
import pytest
# import jsonschema
from common.api_client import MiniShopAPI
from common.test_data import TestData, TestDataBuilder


@pytest.mark.api
@pytest.mark.functional
class TestCheckout:
    """Test checkout endpoints."""
    
    @pytest.fixture(autouse=True)
    def setup(self, config):
        """Setup test fixtures."""
        self.api = MiniShopAPI(config.API_BASE_URL)
        self.data_builder = TestDataBuilder()
    
    @pytest.fixture
    def sample_cart(self):
        """Create a sample cart for testing."""
        items = [
            {"productId": 1, "qty": 2}, 
            {"productId": 2, "qty": 1}   
        ]
        return self.api.add_to_cart(items)
    
    def test_checkout_success(self, sample_cart):
        """Test successful checkout with valid data."""
        # Arrange
        address = self.data_builder.address()
        card = self.data_builder.card_info(valid=True)
        
        # Act
        response = self.api.checkout(
            cart_id=sample_cart["cartId"],
            address=address,
            card=card
        )
        
        # Assert
        assert "orderId" in response
        assert "totalWithTax" in response
        assert "taxApplied" in response
        assert response["totalWithTax"] > sample_cart["totalBeforeTax"]
        assert response["taxApplied"] > 0
        
        # Validate response schema
        # jsonschema.validate(response, TestData.CHECKOUT_RESPONSE_SCHEMA)
    
    def test_checkout_missing_address_returns_422(self, sample_cart):
        """Test checkout with missing address returns 422."""
        # Arrange
        address = self.data_builder.invalid_address()
        card = self.data_builder.card_info(valid=True)
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            self.api.checkout(
                cart_id=sample_cart["cartId"],
                address=address,
                card=card
            )
        
        assert "422" in str(exc_info.value) or "Missing address" in str(exc_info.value)
    
    
    def test_checkout_tax_calculation(self, sample_cart):
        """Test that tax is calculated correctly."""
        # Arrange
        address = self.data_builder.address()
        card = self.data_builder.card_info(valid=True)
        subtotal = sample_cart["totalBeforeTax"]  # 55
        expected_tax_rate = 0.2  # 20%
        expected_tax = subtotal * expected_tax_rate  # 11
        expected_total = subtotal + expected_tax  # 66
        
        # Act
        response = self.api.checkout(
            cart_id=sample_cart["cartId"],
            address=address,
            card=card
        )
        
        # Assert
        assert abs(response["totalWithTax"] - expected_total) < 0.01
        assert abs(response["taxApplied"] - expected_tax) < 0.01
        
    
    def test_checkout_idempotency(self, sample_cart):
        """Test that same checkout payload twice produces same result."""
        # Arrange
        address = self.data_builder.address()
        card = self.data_builder.card_info(valid=True)
        
        # Act
        response1 = self.api.checkout(
            cart_id=sample_cart["cartId"],
            address=address,
            card=card
        )
        
        response2 = self.api.checkout(
            cart_id=sample_cart["cartId"],
            address=address,
            card=card
        )
        
        # Assert
        assert response1["totalWithTax"] == response2["totalWithTax"]
        assert response1["taxApplied"] == response2["taxApplied"]
    
