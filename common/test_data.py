"""
Test data builders and fixtures for MiniShop automation.
"""
from typing import Dict, List, Any
from faker import Faker
import random
import string


class TestDataBuilder:
    """Builder pattern for creating test data."""
    
    def __init__(self):
        self.fake = Faker()
        Faker.seed(42)  # Deterministic data for consistent tests
    
    def user_credentials(self, valid: bool = True) -> Dict[str, str]:
        """Generate user credentials."""
        if valid:
            return {"username": "test", "password": "pass"}
        else:
            return {
                "username": self.fake.user_name(),
                "password": self.fake.password()
            }
    
    def address(self) -> Dict[str, str]:
        """Generate a valid address."""
        return {
            "street": self.fake.street_address(),
            "city": self.fake.city(),
            "state": self.fake.state_abbr(),
            "zip": self.fake.zipcode(),
            "country": self.fake.country()
        }
    
    def invalid_address(self) -> Dict[str, str]:
        """Generate an invalid address (missing required fields)."""
        return {
            "street": "",
            "city": "",
            "state": "",
            "zip": "",
            "country": ""
        }
    
    def card_info(self, valid: bool = True) -> Dict[str, str]:
        """Generate card information."""
        if valid:
            return {
                "number": "4111111111111111",  # Valid test card
                "expiry": "12/25",
                "cvv": "123",
                "name": self.fake.name()
            }
        else:
            return {
                "number": self.fake.credit_card_number(),
                "expiry": "13/20",  # Invalid expiry
                "cvv": "12",  # Invalid CVV length
                "name": ""
            }
    
    def cart_items(self, count: int = 2, product_ids: List[int] = None) -> List[Dict[str, int]]:
        """Generate cart items."""
        if product_ids is None:
            product_ids = [1, 2, 3, 4, 5, 6, 7, 8]  # Available product IDs
        
        items = []
        for _ in range(count):
            items.append({
                "productId": random.choice(product_ids),
                "qty": random.randint(1, 5)
            })
        return items
    
    def single_cart_item(self, product_id: int = 1, quantity: int = 1) -> List[Dict[str, int]]:
        """Generate a single cart item."""
        return [{"productId": product_id, "qty": quantity}]
    
    def duplicate_cart_items(self, product_id: int = 1) -> List[Dict[str, int]]:
        """Generate duplicate cart items to test consolidation."""
        return [
            {"productId": product_id, "qty": 2},
            {"productId": product_id, "qty": 3}
        ]
    
    def invalid_cart_items(self) -> List[Dict[str, int]]:
        """Generate invalid cart items (non-existent product)."""
        return [{"productId": 999, "qty": 1}]
    
    def product_filters(self) -> Dict[str, Any]:
        """Generate product filter parameters."""
        return {
            "category": random.choice(["Clothing", "Accessories", "Electronics"]),
            "minPrice": random.randint(0, 50),
            "maxPrice": random.randint(100, 1000)
        }
    
    def boundary_price_filters(self) -> List[Dict[str, Any]]:
        """Generate boundary price filters for edge case testing."""
        return [
            {"minPrice": 0, "maxPrice": 0},  # No products
            {"minPrice": 1000, "maxPrice": 2000},  # High range
            {"minPrice": 5, "maxPrice": 5},  # Exact match
            {"minPrice": 0, "maxPrice": float('inf')},  # All products
        ]


class TestData:
    """Static test data constants."""
    
    # API endpoints
    LOGIN_ENDPOINT = "/api/login"
    PRODUCTS_ENDPOINT = "/api/products"
    CART_ENDPOINT = "/api/cart"
    CHECKOUT_ENDPOINT = "/api/checkout"
    ORDER_ENDPOINT = "/api/order"
    
    # Expected product data
    EXPECTED_PRODUCTS = [
        {"id": 1, "name": "Shirt", "price": 20.0, "category": "Clothing"},
        {"id": 2, "name": "Hat", "price": 15.0, "category": "Accessories"},
        {"id": 3, "name": "Skirt", "price": 30.0, "category": "Clothing"},
        {"id": 4, "name": "Socks", "price": 5.0, "category": "Clothing"},
        {"id": 5, "name": "Belt", "price": 10.0, "category": "Accessories"},
        {"id": 6, "name": "Jacket", "price": 50.0, "category": "Clothing"},
        {"id": 7, "name": "Phone", "price": 699.0, "category": "Electronics"},
        {"id": 8, "name": "Laptop", "price": 999.0, "category": "Electronics"}
    ]
    
    # Valid test credentials
    VALID_CREDENTIALS = {"username": "test", "password": "pass"}
    INVALID_CREDENTIALS = {"username": "invalid", "password": "wrong"}
    
    # Sample address and card
    SAMPLE_ADDRESS = {
        "street": "123 Test Street",
        "city": "Test City",
        "state": "TS",
        "zip": "12345",
        "country": "Test Country"
    }
    
    SAMPLE_CARD = {
        "number": "4111111111111111",
        "expiry": "12/25",
        "cvv": "123",
        "name": "Test User"
    }
    
    # Expected response schemas
    LOGIN_RESPONSE_SCHEMA = {
        "type": "object",
        "properties": {
            "token": {"type": "string"}
        },
        "required": ["token"]
    }
    
    PRODUCTS_RESPONSE_SCHEMA = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"},
                "price": {"type": "number"},
                "category": {"type": "string"}
            },
            "required": ["id", "name", "price", "category"]
        }
    }
    
    CART_RESPONSE_SCHEMA = {
        "type": "object",
        "properties": {
            "cartId": {"type": "string"},
            "totalBeforeTax": {"type": "number"}
        },
        "required": ["cartId", "totalBeforeTax"]
    }
    
    CHECKOUT_RESPONSE_SCHEMA = {
        "type": "object",
        "properties": {
            "orderId": {"type": "string"},
            "totalWithTax": {"type": "number"},
            "taxApplied": {"type": "number"}
        },
        "required": ["orderId", "totalWithTax", "taxApplied"]
    }
    
    ORDER_RESPONSE_SCHEMA = {
        "type": "object",
        "properties": {
            "orderId": {"type": "string"},
            "items": {"type": "array"},
            "totals": {"type": "number"}
        },
        "required": ["orderId", "items", "totals"]
    }