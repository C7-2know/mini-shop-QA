"""
Authentication API tests for MiniShop.
"""
import pytest
# import jsonschema
from common.api_client import MiniShopAPI
from common.test_data import TestData, TestDataBuilder


@pytest.mark.api
@pytest.mark.smoke
class TestAuthentication:
    """Test authentication endpoints."""
    
    @pytest.fixture(autouse=True)
    def setup(self, config):
        """Setup test fixtures."""
        self.api = MiniShopAPI(config.API_BASE_URL)
        self.data_builder = TestDataBuilder()
    
    def test_login_success(self, config):
        """Test successful login with valid credentials."""
        # Act
        response = self.api.login(
            username=config.VALID_CREDENTIALS["username"],
            password=config.VALID_CREDENTIALS["password"]
        )
        
        # Assert
        assert response["token"] is not None
        assert len(response["token"]) > 0
        
        # Validate response schema
        # jsonschema.validate(response, TestData.LOGIN_RESPONSE_SCHEMA)
    
    def test_login_invalid_credentials(self, config):
        """Test login with invalid credentials returns 401."""
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            self.api.login(
                username=config.INVALID_CREDENTIALS["username"],
                password=config.INVALID_CREDENTIALS["password"]
            )
        
        assert "401" in str(exc_info.value) or "Login failed" in str(exc_info.value)
    
    def test_login_empty_credentials(self):
        """Test login with empty credentials."""
        # Act & Assert
        with pytest.raises(Exception):
            self.api.login(username="", password="")
    
    def test_login_missing_username(self):
        """Test login with missing username."""
        # Act & Assert
        with pytest.raises(Exception):
            self.api.login(username="", password="password")
    
    def test_login_missing_password(self):
        """Test login with missing password."""
        # Act & Assert
        with pytest.raises(Exception):
            self.api.login(username="test", password="")
    
    def test_login_sql_injection_attempt(self):
        """Test login with SQL injection attempt."""
        # Act & Assert
        with pytest.raises(Exception):
            self.api.login(
                username="'; DROP TABLE users; --",
                password="anything"
            )
    
    def test_login_xss_attempt(self):
        """Test login with XSS attempt."""
        # Act & Assert
        with pytest.raises(Exception):
            self.api.login(
                username="<script>alert('xss')</script>",
                password="anything"
            )