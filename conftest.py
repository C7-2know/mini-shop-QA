"""
Global pytest configuration and fixtures for MiniShop automation suite.
"""
import pytest
import requests
from playwright.async_api import async_playwright
import os


# Test configuration
class TestConfig:
    """Test configuration constants."""
    API_BASE_URL = "http://localhost:8000/api"
    UI_BASE_URL = "http://localhost:3000"
    BACKEND_URL = "http://localhost:8000"
    FRONTEND_URL = "http://localhost:3000"
    
    # Test data
    VALID_CREDENTIALS = {"username": "test", "password": "pass"}
    INVALID_CREDENTIALS = {"username": "invalid", "password": "wrong"}
    
    # Test timeouts
    API_TIMEOUT = 10
    UI_TIMEOUT = 30000  # 30 seconds for Playwright
    
    # Test data
    SAMPLE_PRODUCTS = [
        {"id": 1, "name": "Shirt", "price": 20.0, "category": "Clothing"},
        {"id": 2, "name": "Hat", "price": 15.0, "category": "Accessories"},
        {"id": 7, "name": "Phone", "price": 699.0, "category": "Electronics"},
    ]
    
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


@pytest.fixture(scope="session")
def config():
    """Provide test configuration."""
    return TestConfig()


@pytest.fixture(scope="session")
def api_client(config):
    """Create API client with base configuration."""
    session = requests.Session()
    session.timeout = config.API_TIMEOUT
    return session


@pytest.fixture(scope="session")
def backend_health_check(config):
    """Check if backend is running before tests."""
    try:
        response = requests.get(f"{config.BACKEND_URL}/api/health", timeout=5)
        if response.status_code == 200:
            return True
    except requests.exceptions.RequestException:
        pass
    pytest.skip("Backend not available - skipping API tests")


@pytest.fixture(scope="session")
def frontend_health_check(config):
    """Check if frontend is running before tests."""
    try:
        response = requests.get(config.FRONTEND_URL, timeout=5)
        if response.status_code == 200:
            return True
    except requests.exceptions.RequestException:
        pass
    pytest.skip("Frontend not available - skipping UI tests")



def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test location."""
    for item in items:
        # Add markers based on test file location
        if "ui" in str(item.fspath):
            item.add_marker(pytest.mark.ui)
        elif "api" in str(item.fspath):
            item.add_marker(pytest.mark.api)
        
        # Add slow marker for tests that take longer
        if "slow" in item.name:
            item.add_marker(pytest.mark.slow)
