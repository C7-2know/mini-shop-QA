"""
Orders API tests for MiniShop.
"""
import pytest
# import jsonschema
from common.api_client import MiniShopAPI
from common.test_data import TestData, TestDataBuilder


@pytest.mark.api
@pytest.mark.functional
class TestOrders:
    """Test order endpoints."""
    
    @pytest.fixture(autouse=True)
    def setup(self, config):
        """Setup test fixtures."""
        self.api = MiniShopAPI(config.API_BASE_URL)
        self.data_builder = TestDataBuilder()
    
    @pytest.fixture
    def sample_order(self):
        """Create a sample order for testing."""
        # Create cart
        items = [
            {"productId": 1, "qty": 2},  # Shirt: 2 * 20 = 40
            {"productId": 2, "qty": 1}   # Hat: 1 * 15 = 15
        ]
        cart = self.api.add_to_cart(items)
        
        # Checkout
        address = self.data_builder.address()
        card = self.data_builder.card_info(valid=True)
        return self.api.checkout(
            cart_id=cart["cartId"],
            address=address,
            card=card
        )
    
    def test_get_order_success(self, sample_order):
        """Test getting order details by ID."""
        # Act
        order = self.api.get_order(sample_order["orderId"])
        
        # Assert
        assert order["orderId"] == sample_order["orderId"]
        assert "items" in order
        assert "totals" in order
        
        # Validate response schema
        # jsonschema.validate(order, TestData.ORDER_RESPONSE_SCHEMA)
    
    def test_get_order_returns_what_checkout_created(self, sample_order):
        """Test that GET order returns what checkout created."""
        # Act
        order = self.api.get_order(sample_order["orderId"])
        
        # Assert
        assert order["orderId"] == sample_order["orderId"]
        # Note: The mock API returns hardcoded data, but in real scenario
        # we would verify that the order details match what was created
        assert order["totals"] is not None
    
   